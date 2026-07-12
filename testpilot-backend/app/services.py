"""核心服务层：AI 调用 + 脚本执行"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx

from .config import Settings, get_settings
from .models import (
    AnalyzeResponse,
    FeaturePoint,
    GenerateResponse,
    GeneratedCase,
    RunResponse,
)
from .prompts import ANALYZE_PROMPT, GENERATE_PROMPT, SYSTEM_PROMPT


# ============================================================
# AI 服务：封装 DeepSeek API 调用
# ============================================================

class AIService:
    """DeepSeek API 调用封装"""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.deepseek_base_url.rstrip("/")
        self.timeout = 120.0  # 生成脚本可能较慢

    async def chat(self, user_prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """调用 DeepSeek Chat API，返回文本内容"""
        if not self.settings.has_api_key:
            raise RuntimeError(
                "未配置 DEEPSEEK_API_KEY，请在 .env 文件中填写有效的 API Key"
            )

        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.deepseek_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 12000,
            "response_format": {"type": "json_object"},
        }

        max_retries = 5
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, trust_env=False) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()

                content = data["choices"][0]["message"]["content"]
                
                text = content.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict) and "feature_points" in parsed:
                        if len(parsed["feature_points"]) >= 2:
                            return text
                    if isinstance(parsed, dict) and "cases" in parsed:
                        if len(parsed["cases"]) >= 1:
                            return text
                    if isinstance(parsed, dict):
                        return text
                except json.JSONDecodeError:
                    pass
                
                if text.startswith("{"):
                    brace_count = 1
                    for i, char in enumerate(text[1:], 1):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                fixed_text = text[:i+1]
                                try:
                                    json.loads(fixed_text)
                                    return fixed_text
                                except json.JSONDecodeError:
                                    pass
                                    break
                
                raise RuntimeError(f"AI 返回内容不是有效的 JSON 格式（尝试 {attempt + 1}/{max_retries}）")
                
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(3)
                else:
                    raise

        return data["choices"][0]["message"]["content"]

    async def analyze_requirement(
        self, requirement_text: str, app_url: str | None = None
    ) -> AnalyzeResponse:
        """需求分析：需求文本 → 功能点列表"""
        prompt = ANALYZE_PROMPT.format(
            requirement_text=requirement_text,
            app_url=app_url or "未提供",
        )
        raw = await self.chat(prompt)
        data = self._parse_json(raw)

        feature_points = []
        for fp in data.get("feature_points", []):
            test_dims = fp.get("test_dimensions", [])
            if isinstance(test_dims, str):
                test_dims = [d.strip() for d in test_dims.split() if d.strip()]
            elif not isinstance(test_dims, list):
                test_dims = []
            
            feature_points.append(FeaturePoint(
                name=fp.get("name", "未命名功能"),
                priority=fp.get("priority", "P2"),
                test_dimensions=test_dims,
                business_logic=fp.get("business_logic", ""),
                risk_hint=fp.get("risk_hint", ""),
            ))

        return AnalyzeResponse(
            feature_points=feature_points,
            summary=data.get("summary", ""),
            estimated_case_count=data.get("estimated_case_count", len(feature_points) * 3),
            raw=raw,
        )

    async def generate_scripts(
        self,
        feature_points: list[FeaturePoint],
        app_url: str = "",
    ) -> GenerateResponse:
        """脚本生成：功能点 → Playwright 脚本"""
        s = self.settings
        fp_json = json.dumps(
            [fp.model_dump() for fp in feature_points], ensure_ascii=False, indent=2
        )
        test_account = "未提供"
        if s.test_username:
            test_account = f"用户名: {s.test_username} / 密码: {s.test_password or '***'}"

        base_prompt = GENERATE_PROMPT.format(
            feature_points_json=fp_json,
            app_name="TodoMVC",
            app_url=app_url or s.target_app_url or "未提供",
            login_url=s.login_url or "未提供",
            test_account=test_account,
            test_username=s.test_username or "",
            test_password=s.test_password or "",
        )

        max_attempts = 3
        validation_errors: list[str] = []
        raw = ""
        cases: list[GeneratedCase] = []

        for attempt in range(max_attempts):
            prompt = base_prompt
            if validation_errors:
                prompt += (
                    "\n\n# 上次生成不合格，请修正以下问题后重新生成：\n"
                    + "\n".join(f"- {e}" for e in validation_errors)
                )

            raw = await self.chat(prompt)
            data = self._parse_json(raw)
            cases = []
            validation_errors = []

            for c in data.get("cases", []):
                script = self._strip_code_fence(c.get("script", ""))
                errors = self._validate_script(script)
                if errors:
                    validation_errors.extend(
                        [f"[{c.get('module', 'unknown')}] {e}" for e in errors]
                    )
                cases.append(
                    GeneratedCase(
                        title=c.get("title", "未命名用例"),
                        module=c.get("module", ""),
                        priority=c.get("priority", "P1"),
                        precondition=c.get("precondition", ""),
                        steps=c.get("steps", []),
                        expected=c.get("expected", ""),
                        script=script,
                        stability_score=c.get("stability_score", 80),
                    )
                )

            if not validation_errors:
                break

        if validation_errors:
            raw += (
                "\n\n<!-- validation_errors: "
                + json.dumps(validation_errors, ensure_ascii=False)
                + " -->"
            )

        return GenerateResponse(cases=cases, raw=raw)

    @staticmethod
    def _validate_script(script: str) -> list[str]:
        """校验脚本结构，返回错误列表（空列表表示合格）"""
        errors: list[str] = []
        if not script.strip():
            errors.append("脚本内容为空")
            return errors

        if "test.describe" not in script:
            errors.append("缺少 test.describe 分组")
        if "test.beforeEach" not in script:
            errors.append("缺少 test.beforeEach 前置条件")
        if script.count("test(") < 2:
            errors.append("至少需要 2 个 test() 用例")
        if "expect(" not in script:
            errors.append("缺少 expect() 断言")

        forbidden = [
            ("waitForTimeout", "禁止使用 waitForTimeout"),
            (".css-", "禁止使用 CSS class hash 选择器"),
            ("nth-child", "禁止使用 nth-child 选择器"),
        ]
        for pattern, msg in forbidden:
            if pattern in script:
                errors.append(msg)

        return errors

    @staticmethod
    def _parse_json(text: str) -> dict:
        """解析 AI 返回的 JSON"""
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"JSON 解析失败: {e}\n原始内容: {text[:500]}")

    @staticmethod
    def _strip_code_fence(code: str) -> str:
        """去掉脚本内容外层的 markdown 代码块标记"""
        code = code.strip()
        if code.startswith("```"):
            code = re.sub(r"^```(?:typescript|ts|javascript|js)?\s*", "", code)
            code = re.sub(r"\s*```$", "", code)
        return code.strip()


# ============================================================
# 执行服务：运行 Playwright 脚本
# ============================================================

class ExecutionService:
    """Playwright 脚本执行器"""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def run_script(
        self,
        script: str,
        app_url: str | None = None,
        timeout: int | None = None,
    ) -> RunResponse:
        """执行 Playwright 脚本并返回结果"""
        playwright_root = self.settings.playwright_root
        run_dir = self.settings.runtime_dir / uuid.uuid4().hex[:8]
        run_dir.mkdir(parents=True, exist_ok=True)
        spec_file = run_dir / "test.spec.ts"

        # 替换脚本中的 URL 占位（如果提供了 app_url）
        script_content = script
        if app_url:
            # 简单替换常见的 localhost 占位
            script_content = script_content.replace(
                "http://localhost:3000", app_url
            ).replace("http://localhost:8080", app_url)

        spec_file.write_text(script_content, encoding="utf-8")

        # 从 Playwright 根目录执行，使用相对路径以便正确加载 node_modules
        spec_rel = spec_file.relative_to(playwright_root).as_posix()
        cmd = self._build_command(spec_rel, run_dir, timeout)
        start = time.time()
        test_count = max(1, len(re.findall(r"\btest\s*\(\s*['\"]", script_content)))
        proc_timeout = timeout or int(self.settings.browser_timeout / 1000 * test_count + 60)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=proc_timeout,
                cwd=str(playwright_root),
            )
            duration_ms = int((time.time() - start) * 1000)
            passed = proc.returncode == 0

            screenshots = self._collect_screenshots(run_dir)
            screenshot_urls = []
            for s in screenshots:
                screenshot_path = Path(s)
                if screenshot_path.is_relative_to(self.settings.runtime_dir):
                    rel_path = screenshot_path.relative_to(self.settings.runtime_dir).as_posix()
                    screenshot_urls.append(f"/screenshots/{rel_path}")
                else:
                    screenshot_urls.append(s)

            return RunResponse(
                passed=passed,
                duration_ms=duration_ms,
                stdout=proc.stdout[-8000:] if len(proc.stdout) > 8000 else proc.stdout,
                stderr=proc.stderr[-8000:] if len(proc.stderr) > 8000 else proc.stderr,
                screenshots=screenshot_urls,
                error=None if passed else self._extract_error(proc.stderr, proc.stdout),
            )
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start) * 1000)
            return RunResponse(
                passed=False,
                duration_ms=duration_ms,
                stdout="",
                stderr="执行超时",
                error=f"脚本执行超时（{proc_timeout}s，共 {test_count} 个 test）",
            )
        except FileNotFoundError:
            return RunResponse(
                passed=False,
                duration_ms=0,
                stdout="",
                stderr="未找到 npx 命令，请确保已安装 Node.js",
                error="环境错误：未安装 Node.js 或 npx 不在 PATH 中",
            )

    def _build_command(
        self, spec_rel_path: str, work_dir: Path, timeout: int | None
    ) -> list[str]:
        """构建 playwright test 命令"""
        npx = shutil.which("npx")
        if not npx:
            raise FileNotFoundError("npx")
        
        config_rel = Path(
            self._write_config(work_dir)
        ).relative_to(self.settings.playwright_root).as_posix()
        
        cmd = [
            npx,
            "playwright",
            "test",
            spec_rel_path,
            "--reporter=line",
            "--config", config_rel,
        ]
        if timeout:
            cmd.extend(["--timeout", str(timeout)])

        return cmd

    def _write_config(self, work_dir: Path) -> str:
        """写入 playwright.config.ts（配置截图和浏览器）"""
        storage_state = self.settings.storage_state_path if self.settings.storage_state_path else None
        storage_line = f"storageState: '{storage_state}'," if storage_state else ""
        config_content = f"""import {{ defineConfig }} from '@playwright/test';

export default defineConfig({{
  outputDir: '.test-results',
  use: {{
    browserName: '{self.settings.browser_type}',
    screenshot: 'on',
    video: 'retain-on-failure',
    {storage_line}
  }},
}});
"""
        config_path = work_dir / "playwright.config.ts"
        config_path.write_text(config_content, encoding="utf-8")
        return str(config_path)

    @staticmethod
    def _collect_screenshots(work_dir: Path) -> list[str]:
        """收集执行过程中产生的截图"""
        screenshots = []
        for pattern in ["*.png", "test-results/**/*.png", ".test-results/**/*.png"]:
            screenshots.extend(str(p) for p in work_dir.glob(pattern))
        return screenshots

    @staticmethod
    def _extract_error(stderr: str, stdout: str) -> str:
        """从输出中提取关键错误信息"""
        for line in (stderr + "\n" + stdout).splitlines():
            line = line.strip()
            if line.startswith("Error:") or "error" in line.lower()[:20]:
                return line[:500]
        # 兜底：返回 stderr 最后几行
        return stderr[-500:] if stderr else stdout[-500:]
