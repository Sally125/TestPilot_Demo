#!/usr/bin/env python3
"""
Playwright 测试执行脚本

功能：
1. 接收 .spec.ts 文件路径
2. 运行 npx playwright test
3. 解析输出，提取 pass/fail 结果
4. 生成 JSON 格式报告

用法：
    python execute_tests.py <spec_file_path>
    python execute_tests.py <directory_path>
"""

import subprocess
import sys
import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime


class PlaywrightExecutor:
    def __init__(self, playwright_root: Path = None):
        self.playwright_root = playwright_root or Path(os.getcwd())

    def run(self, target_path: str) -> dict:
        """运行测试并返回结果"""
        target = Path(target_path)
        
        if not target.exists():
            return self._error(f"路径不存在: {target_path}")
        
        if target.is_file() and target.suffix == ".spec.ts":
            return self._run_single_file(target)
        elif target.is_dir():
            return self._run_directory(target)
        else:
            return self._error(f"不支持的路径类型: {target_path}")

    def _run_single_file(self, spec_file: Path) -> dict:
        """运行单个测试文件"""
        try:
            spec_rel = spec_file.relative_to(self.playwright_root).as_posix()
        except ValueError:
            spec_rel = spec_file.as_posix()
        return self._execute_command(spec_rel)

    def _run_directory(self, dir_path: Path) -> dict:
        """运行目录下所有测试文件"""
        spec_files = sorted(dir_path.glob("*.spec.ts"))
        if not spec_files:
            return self._error(f"目录下没有找到 .spec.ts 文件: {dir_path}")
        
        try:
            dir_rel = dir_path.relative_to(self.playwright_root).as_posix()
        except ValueError:
            dir_rel = dir_path.as_posix()
        return self._execute_command(dir_rel)

    def _execute_command(self, target_rel: str) -> dict:
        """执行 Playwright 命令"""
        npx = shutil.which("npx")
        if not npx:
            return self._error("未找到 npx 命令，请确保已安装 Node.js")

        cmd = [
            npx,
            "playwright",
            "test",
            target_rel,
            "--reporter=json",
            "--output=test-results",
        ]

        start_time = datetime.now()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(self.playwright_root),
            )
        except subprocess.TimeoutExpired:
            return self._error("测试执行超时")
        except Exception as e:
            return self._error(f"执行失败: {str(e)}")

        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        return self._parse_output(proc, duration_ms)

    def _parse_output(self, proc: subprocess.CompletedProcess, duration_ms: int) -> dict:
        """解析 Playwright JSON 输出"""
        try:
            report = json.loads(proc.stdout)
            return self._build_report(report, duration_ms)
        except json.JSONDecodeError:
            return self._parse_text_output(proc, duration_ms)

    def _build_report(self, report: dict, duration_ms: int) -> dict:
        """从 JSON 报告构建结果"""
        results = []
        passed_count = 0
        failed_count = 0

        def parse_suites(suites):
            nonlocal passed_count, failed_count
            for suite in suites:
                for spec in suite.get("specs", []):
                    for test in spec.get("tests", []):
                        for result in test.get("results", []):
                            test_name = spec.get("title", "")
                            status = result.get("status", "unknown")
                            duration = result.get("duration", 0)
                            errors = []

                            for error in result.get("errors", []):
                                errors.append(error.get("message", ""))

                            if status == "passed":
                                passed_count += 1
                            else:
                                failed_count += 1

                            results.append({
                                "name": test_name,
                                "status": status,
                                "duration_ms": duration,
                                "errors": errors,
                            })

                parse_suites(suite.get("suites", []))

        parse_suites(report.get("suites", []))

        return {
            "success": True,
            "total": passed_count + failed_count,
            "passed": passed_count,
            "failed": failed_count,
            "duration_ms": duration_ms,
            "pass_rate": round((passed_count / (passed_count + failed_count)) * 100, 2) if (passed_count + failed_count) > 0 else 0,
            "results": results,
            "stdout": "",
            "stderr": "",
        }

    def _parse_text_output(self, proc: subprocess.CompletedProcess, duration_ms: int) -> dict:
        """从文本输出解析结果（降级方案）"""
        stdout = proc.stdout
        stderr = proc.stderr
        output = stdout + stderr

        # 提取测试数量
        match = re.search(r"Running (\d+) tests", output)
        total = int(match.group(1)) if match else 0

        # 提取失败数量
        match = re.search(r"(\d+) failed", output)
        failed_count = int(match.group(1)) if match else 0

        passed_count = total - failed_count

        # 提取失败用例详情
        results = []
        failed_pattern = re.compile(r"(\d+\)) (.+?)\n((?:.|\n)*?)(?=\n\n|$)", re.MULTILINE)
        for match in failed_pattern.finditer(output):
            name = match.group(2).strip()
            errors = match.group(3).strip()[:500]
            results.append({
                "name": name,
                "status": "failed",
                "duration_ms": 0,
                "errors": [errors],
            })

        return {
            "success": True,
            "total": total,
            "passed": passed_count,
            "failed": failed_count,
            "duration_ms": duration_ms,
            "pass_rate": round((passed_count / total) * 100, 2) if total > 0 else 0,
            "results": results,
            "stdout": stdout[-2000:] if len(stdout) > 2000 else stdout,
            "stderr": stderr[-2000:] if len(stderr) > 2000 else stderr,
        }

    def _error(self, message: str) -> dict:
        """生成错误结果"""
        return {
            "success": False,
            "error": message,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "duration_ms": 0,
            "pass_rate": 0,
            "results": [],
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python execute_tests.py <spec_file_path|directory_path>")
        sys.exit(1)

    target_path = sys.argv[1]
    executor = PlaywrightExecutor()
    result = executor.run(target_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()