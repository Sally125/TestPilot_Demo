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
from urllib.parse import quote

import httpx

from .config import Settings, get_settings
from .models import (
    AnalyzeResponse,
    CoverageMatrix,
    CoverageMatrixItem,
    DesignTestCasesResponse,
    DesignedTestCase,
    FeaturePoint,
    GenerateResponse,
    GeneratedCase,
    ReviewResponse,
    ReviewSuggestion,
    RunResponse,
    TestCaseData,
    TestCaseStep,
    TestCaseSummary,
)
from .prompts import ANALYZE_PROMPT, GENERATE_PROMPT, REVIEW_PROMPT, SYSTEM_PROMPT, TESTCASE_DESIGN_PROMPT_PART1, TESTCASE_DESIGN_PROMPT_PART2, TESTCASE_DESIGN_PROMPT_JSON_TEMPLATE


# ============================================================
# AI 服务：封装 DeepSeek API 调用
# ============================================================

class AIService:
    """DeepSeek API 调用封装"""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.deepseek_base_url.rstrip("/")
        self.timeout = 900.0  # 生成脚本可能较慢，给足时间避免超时（15分钟）

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
            "temperature": 0.7,
            "max_tokens": 32000,
            "response_format": {"type": "json_object"},
            "disable_reasoning": True,
        }

        max_retries = 2
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, trust_env=False) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    
                    if resp.status_code == 503:
                        raise RuntimeError(
                            f"AI服务暂时不可用（503），请稍后重试。URL: {url}"
                        )

                    if resp.status_code == 401:
                        raise RuntimeError(
                            f"API Key 无效（401），请检查 .env 文件中的 DEEPSEEK_API_KEY 配置。"
                        )

                    if resp.status_code == 403:
                        # 尝试读取响应体中的错误信息
                        forbidden_detail = ""
                        try:
                            err_body = resp.json()
                            forbidden_detail = err_body.get("error", {}).get("message", "") or str(err_body)
                        except Exception:
                            forbidden_detail = resp.text[:300] if resp.text else ""
                        raise RuntimeError(
                            f"AI服务拒绝访问（403 Forbidden）。"
                            f"常见原因：API Key 已失效、账户余额不足、或请求被服务方拦截。"
                            f"请检查 API 服务状态和账户余额。"
                            + (f" 服务方返回：{forbidden_detail}" if forbidden_detail else "")
                        )

                    if resp.status_code == 404:
                        raise RuntimeError(
                            f"API 路径不存在（404），请检查 DEEPSEEK_BASE_URL 配置。当前URL: {url}"
                        )
                    
                    resp.raise_for_status()
                    data = resp.json()

                print(f"[DEBUG] API Response - attempt {attempt+1}:")
                print(f"[DEBUG] choices count: {len(data.get('choices', []))}")
                if data.get('choices'):
                    choice = data['choices'][0]
                    print(f"[DEBUG] finish_reason: {choice.get('finish_reason')}")
                    print(f"[DEBUG] message keys: {list(choice.get('message', {}).keys())}")
                    print(f"[DEBUG] content type: {type(choice.get('message', {}).get('content'))}")
                    print(f"[DEBUG] content repr: {repr(choice.get('message', {}).get('content'))[:500]}")
                    print(f"[DEBUG] content len: {len(str(choice.get('message', {}).get('content', '')))}")
                print(f"[DEBUG] usage: {data.get('usage', {})}")

                content = data["choices"][0]["message"]["content"]
                finish_reason = data["choices"][0].get("finish_reason", "unknown")
                print(f"[DEBUG] finish_reason: {finish_reason}, content_length: {len(content) if content else 0}")

                # 截断检测：finish_reason="length" 表示响应被 max_tokens 截断，JSON 必然不完整
                if finish_reason == "length":
                    print(f"[DEBUG] 响应被 max_tokens 截断，content_length: {len(content) if content else 0}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                    raise RuntimeError(
                        f"AI 响应被 max_tokens 截断（finish_reason=length），"
                        f"返回内容不完整无法解析。请减少用例数量或缩短脚本内容后重试。"
                    )

                if content is None:
                    print(f"[DEBUG] content is None, finish_reason: {finish_reason}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                    raise RuntimeError(f"AI 返回内容为空（尝试 {attempt + 1}/{max_retries}）。finish_reason: {finish_reason}")
                
                if not content.strip():
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                    raise RuntimeError(f"AI 返回内容为空（尝试 {attempt + 1}/{max_retries}）")
                
                text = content.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                
                text = text.replace('\r\n', '\n')
                
                text = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\u0075', text)
                
                def try_parse_json(input_text):
                    try:
                        parsed = json.loads(input_text)
                        if isinstance(parsed, (dict, list)):
                            return parsed, input_text
                    except json.JSONDecodeError:
                        pass
                    return None, None
                
                parsed, result = try_parse_json(text)
                if parsed is not None:
                    return result
                
                def find_matching_brace(s, start_char, end_char):
                    if not s.startswith(start_char):
                        return None
                    count = 1
                    in_string = False
                    escape = False
                    for i, char in enumerate(s[1:], 1):
                        if escape:
                            escape = False
                            continue
                        if char == '\\':
                            escape = True
                            continue
                        if char == '"':
                            in_string = not in_string
                            continue
                        if not in_string:
                            if char == start_char:
                                count += 1
                            elif char == end_char:
                                count -= 1
                                if count == 0:
                                    return s[:i+1]
                    return None
                
                matched_json = find_matching_brace(text, '{', '}')
                if matched_json:
                    parsed, result = try_parse_json(matched_json)
                    if parsed is not None:
                        return result
                
                matched_json = find_matching_brace(text, '[', ']')
                if matched_json:
                    parsed, result = try_parse_json(matched_json)
                    if parsed is not None:
                        return result
                
                fixed_text = text
                fixed_text = fixed_text.replace('"/', '"⁄')
                fixed_text = fixed_text.replace('"\\', '"‹')
                fixed_text = fixed_text.replace('\\"', '"')
                fixed_text = re.sub(r'(?<!\\)"([^"]*?)"/', '"\\1⁄"', fixed_text)
                fixed_text = re.sub(r'(?<!\\)"([^"]*?)"\\', '"\\1‹"', fixed_text)
                
                parsed, result = try_parse_json(fixed_text)
                if parsed is not None:
                    return result
                
                try:
                    import ast
                    parsed = ast.literal_eval(text)
                    if isinstance(parsed, (dict, list)):
                        return json.dumps(parsed, ensure_ascii=False)
                except (SyntaxError, ValueError):
                    pass
                
                try:
                    import ast
                    fixed_text = text.replace('\"', '"').replace('\\"', '"')
                    parsed = ast.literal_eval(fixed_text)
                    if isinstance(parsed, (dict, list)):
                        return json.dumps(parsed, ensure_ascii=False)
                except (SyntaxError, ValueError):
                    pass
                
                try:
                    import ast
                    fixed_text = re.sub(r'(?<!\\)"', "'", text)
                    parsed = ast.literal_eval(fixed_text)
                    if isinstance(parsed, (dict, list)):
                        return json.dumps(parsed, ensure_ascii=False)
                except (SyntaxError, ValueError):
                    pass
                
                try:
                    import ast
                    parsed = ast.literal_eval(text.replace('"', "'"))
                    if isinstance(parsed, (dict, list)):
                        return json.dumps(parsed, ensure_ascii=False)
                except (SyntaxError, ValueError):
                    pass
                
                try:
                    json_match = re.search(r'\{[\s\S]*\}', text, re.DOTALL)
                    if json_match:
                        parsed, result = try_parse_json(json_match.group(0))
                        if parsed is not None:
                            return result
                except Exception:
                    pass
                
                try:
                    lines = text.split('\n')
                    valid_lines = []
                    for line in lines:
                        if line.strip():
                            valid_lines.append(line)
                    fixed_text = '\n'.join(valid_lines)
                    parsed, result = try_parse_json(fixed_text)
                    if parsed is not None:
                        return result
                except Exception:
                    pass
                
                try:
                    fixed_text = re.sub(r'\\(?=")', '', text)
                    parsed, result = try_parse_json(fixed_text)
                    if parsed is not None:
                        return result
                except Exception:
                    pass
                
                text_length = len(text)
                raise RuntimeError(f"AI 返回内容不是有效的 JSON 格式（尝试 {attempt + 1}/{max_retries}）。响应长度: {text_length}。原始响应前1000字符: {text[:1000]}")
                
            except httpx.ConnectError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise RuntimeError(
                        f"无法连接到 AI 服务，请检查网络连接或 API 地址配置。URL: {url}, 错误: {str(e)}"
                    )
            except httpx.TimeoutException as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise RuntimeError(
                        f"AI 服务请求超时，请检查网络或稍后重试。URL: {url}"
                    )
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise

        return data["choices"][0]["message"]["content"]

    async def chat_stream(self, user_prompt: str, system_prompt: str = SYSTEM_PROMPT):
        """调用 DeepSeek Chat API，流式返回内容"""
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
            "temperature": 0.7,
            "max_tokens": 32000,
            "response_format": {"type": "json_object"},
            "stream": True,
        }

        max_retries = 2
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, trust_env=False) as client:
                    async with client.stream("POST", url, headers=headers, json=payload) as resp:
                        if resp.status_code == 503:
                            raise RuntimeError(
                                f"AI服务暂时不可用（503），请稍后重试。URL: {url}"
                            )

                        if resp.status_code == 401:
                            raise RuntimeError(
                                f"API Key 无效（401），请检查 .env 文件中的 DEEPSEEK_API_KEY 配置。"
                            )

                        if resp.status_code == 403:
                            # 403 通常是频率限制或临时拦截，读取错误详情并重试
                            forbidden_detail = ""
                            try:
                                body = await resp.aread()
                                forbidden_detail = body.decode("utf-8", errors="replace")[:300]
                            except Exception:
                                pass
                            if attempt < max_retries - 1:
                                await asyncio.sleep(3)
                                raise httpx.ConnectError(
                                    f"403 Forbidden (重试中): {forbidden_detail}"
                                )
                            raise RuntimeError(
                                f"AI服务拒绝访问（403 Forbidden）。"
                                f"常见原因：请求频率过高、API Key 已失效、账户余额不足。"
                                f"请稍后重试或检查 API 服务状态。"
                                + (f" 服务方返回：{forbidden_detail}" if forbidden_detail else "")
                            )

                        if resp.status_code == 404:
                            raise RuntimeError(
                                f"API 路径不存在（404），请检查 DEEPSEEK_BASE_URL 配置。当前URL: {url}"
                            )

                        resp.raise_for_status()
                        async for line in resp.aiter_lines():
                            if line.strip().startswith("data:"):
                                data_str = line.strip()[5:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    choices = data.get("choices", [])
                                    if choices and len(choices) > 0:
                                        delta = choices[0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield content
                                except (json.JSONDecodeError, KeyError, IndexError):
                                    continue
                return
            except httpx.ConnectError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise RuntimeError(
                        f"无法连接到 AI 服务，请检查网络连接或 API 地址配置。URL: {url}, 错误: {str(e)}"
                    )
            except httpx.TimeoutException as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise RuntimeError(
                        f"AI 服务请求超时，请检查网络或稍后重试。URL: {url}"
                    )
            except RuntimeError:
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise RuntimeError(
                        f"AI 服务请求失败: {type(e).__name__}: {str(e)}"
                    )

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

    def _deduplicate_test_cases(self, test_cases: list) -> list:
        """去重测试用例：保留1条最完整的正向用例，移除所有其他正向用例"""
        if not test_cases:
            return test_cases
        
        positive_cases = []
        negative_cases = []
        
        negative_keywords = ['错误', '失败', '异常', '边界', '拒绝', '提示', '为空', '无效', '不跳转']
        
        for tc in test_cases:
            tc_type = getattr(tc, 'type', '')
            title = getattr(tc, 'title', '')
            
            is_negative = False
            
            if tc_type in ['异常输入测试', '边界值测试', '异常测试']:
                is_negative = True
            else:
                for kw in negative_keywords:
                    if kw in title:
                        is_negative = True
                        break
            
            if is_negative:
                negative_cases.append(tc)
            else:
                positive_cases.append(tc)
        
        if not positive_cases:
            return test_cases
        
        best_positive = None
        max_fields = 0
        
        for tc in positive_cases:
            test_data = getattr(tc, 'test_data', None)
            if test_data:
                if isinstance(test_data, dict):
                    input_values = test_data.get('input_values', [])
                else:
                    input_values = getattr(test_data, 'input_values', [])
                field_count = len(input_values)
                
                if field_count > max_fields:
                    max_fields = field_count
                    best_positive = tc
        
        if not best_positive:
            best_positive = positive_cases[0]
        
        filtered_cases = [best_positive]
        filtered_cases.extend(negative_cases)
        
        for i, tc in enumerate(filtered_cases):
            tc.id = f"TC-{i+1:03d}"
        
        return filtered_cases

    async def design_test_cases(
        self,
        feature_points: list[FeaturePoint],
    ) -> DesignTestCasesResponse:
        """测试用例设计：功能点 → 结构化测试用例"""
        fp_json = json.dumps(
            [{"id": f"FP-{i+1:03d}", **fp.model_dump()} for i, fp in enumerate(feature_points)],
            ensure_ascii=False,
            indent=2
        )
        from datetime import datetime
        generation_time = datetime.now().isoformat()
        
        prompt = TESTCASE_DESIGN_PROMPT_PART1 + TESTCASE_DESIGN_PROMPT_JSON_TEMPLATE + TESTCASE_DESIGN_PROMPT_PART2.format(
            feature_points_json=fp_json,
        )

        raw = await self.chat(prompt)
        data = self._parse_json(raw)

        if isinstance(data, list):
            data = {"test_cases": data}

        test_cases = []
        for tc in data.get("test_cases", []):
            if not isinstance(tc, dict):
                print(f"[DEBUG] design_test_cases - tc is not dict: {type(tc)}, value: {tc}")
                continue
            
            steps = []
            for s in tc.get("steps", []):
                if isinstance(s, dict):
                    steps.append(TestCaseStep(
                        step=s.get("step", 0),
                        action=s.get("action", ""),
                        expected_result=s.get("expected_result", ""),
                        page_element=s.get("page_element", ""),
                    ))
                elif isinstance(s, str):
                    steps.append(TestCaseStep(
                        step=len(steps) + 1,
                        action=s,
                        expected_result="",
                        page_element="",
                    ))
            
            test_data = tc.get("test_data", {})
            if not isinstance(test_data, dict):
                test_data = {}
            input_values = test_data.get("input_values", [])
            
            if isinstance(input_values, list):
                converted_values = []
                for idx, val in enumerate(input_values):
                    if isinstance(val, dict):
                        converted_values.append(val)
                    elif isinstance(val, str):
                        converted_values.append({"field": f"参数{idx+1}", "value": val})
                    else:
                        converted_values.append({"field": f"参数{idx+1}", "value": str(val)})
                input_values = converted_values
            
            test_cases.append(DesignedTestCase(
                id=tc.get("id", f"TC-{len(test_cases)+1:03d}"),
                title=tc.get("title", "未命名用例"),
                source_feature_id=tc.get("source_feature_id", ""),
                source_feature_name=tc.get("source_feature_name", ""),
                priority=tc.get("priority", "P1"),
                type=tc.get("type", "功能测试"),
                module=tc.get("module", ""),
                preconditions=tc.get("preconditions", ""),
                test_data=TestCaseData(
                    description=test_data.get("description", ""),
                    input_values=input_values,
                ),
                steps=steps,
                expected_result=tc.get("expected_result", ""),
                verification_method=tc.get("verification_method", ""),
                tags=tc.get("tags", []),
                notes=tc.get("notes", ""),
            ))

        test_cases = self._deduplicate_test_cases(test_cases)

        summary_data = data.get("testcase_summary", {})
        summary = TestCaseSummary(
            requirement_title=summary_data.get("requirement_title", ""),
            total_feature_points=summary_data.get("total_feature_points", len(feature_points)),
            total_test_cases=summary_data.get("total_test_cases", len(test_cases)),
            p0_cases=summary_data.get("p0_cases", sum(1 for tc in test_cases if tc.priority == "P0")),
            p1_cases=summary_data.get("p1_cases", sum(1 for tc in test_cases if tc.priority == "P1")),
            p2_cases=summary_data.get("p2_cases", sum(1 for tc in test_cases if tc.priority == "P2")),
            generation_time=summary_data.get("generation_time", generation_time),
        )

        coverage_matrix_data = data.get("coverage_matrix", {})
        coverage_matrix = CoverageMatrix(
            description=coverage_matrix_data.get("description", "功能点覆盖矩阵"),
            matrix=[],
        )
        for item in coverage_matrix_data.get("matrix", []):
            coverage_matrix.matrix.append(CoverageMatrixItem(
                feature_id=item.get("feature_id", ""),
                feature_name=item.get("feature_name", ""),
                covering_cases=item.get("covering_cases", []),
                covered_dimensions=item.get("covered_dimensions", []),
            ))

        return DesignTestCasesResponse(
            testcase_summary=summary,
            test_cases=test_cases,
            coverage_matrix=coverage_matrix,
            raw=raw,
        )

    async def generate_scripts(
        self,
        test_cases: list[DesignedTestCase],
        app_url: str = "",
        storage_state_path: str | None = None,
    ) -> GenerateResponse:
        """脚本生成：测试用例 → Playwright 脚本（含稳定性检测）"""
        from .stability_checker import StabilityChecker
        
        s = self.settings
        
        if not app_url:
            raise RuntimeError("应用URL未配置，请在项目设置中填写被测应用的URL（如 http://localhost:3001）")

        test_account = "未提供"
        if s.test_username:
            test_account = f"用户名: {s.test_username} / 密码: {s.test_password or '***'}"

        app_name = "应用系统"
        if test_cases:
            modules = set()
            for tc in test_cases:
                if tc.module:
                    modules.add(tc.module)
            if modules:
                app_name = ", ".join(list(modules)[:3])
        
        validation_errors: list[str] = []
        raw = ""
        cases: list[GeneratedCase] = []
        checker = StabilityChecker()

        tc_json = json.dumps([tc.model_dump() for tc in test_cases], ensure_ascii=False, indent=2)
        
        base_prompt = GENERATE_PROMPT.format(
            test_cases_json=tc_json,
            app_name=app_name,
            app_url=app_url,
            login_url=s.login_url or app_url,
            test_account=test_account,
            test_username=s.test_username or "",
            test_password=s.test_password or "",
            page_context="# 页面快照（暂未启用）",
        )

        prompt = base_prompt
        tc_raw = await self.chat(prompt)
        raw += tc_raw + "\n"
        
        try:
            data = self._parse_json(tc_raw)
            scripts = data.get("scripts", [])
            if scripts:
                for i, c in enumerate(scripts):
                    tc = test_cases[i] if i < len(test_cases) else None
                    script = self._strip_code_fence(c.get("script", ""))
                    errors = self._validate_script(script)
                    if errors:
                        validation_errors.extend(
                            [f"[{tc.module or 'unknown'}] {e}" for e in errors]
                        )
                    
                    stability_check_result = checker.analyze(script, c.get("case_title", tc.title if tc else ""))
                    
                    cases.append(
                        GeneratedCase(
                            title=c.get("case_title", tc.title if tc else ""),
                            module=c.get("module", tc.module or "" if tc else ""),
                            priority=c.get("priority", tc.priority if tc else "P1"),
                            precondition="",
                            steps=[],
                            expected="",
                            script=script,
                            stability_score=stability_check_result.get("overall_score", c.get("stability_score", 80)),
                            stability_checks=stability_check_result.get("checks"),
                            stability_issues=stability_check_result.get("issues", []),
                        )
                    )
            else:
                validation_errors.append("未生成任何脚本")
        except Exception as e:
            validation_errors.append(f"脚本生成失败 - {str(e)}")

        if validation_errors:
            raw += (
                "\n\n<!-- validation_errors: "
                + json.dumps(validation_errors, ensure_ascii=False)
                + " -->"
            )
            raise ValueError(f"脚本生成验证失败: {'; '.join(validation_errors[:5])}")

        return GenerateResponse(cases=cases, raw=raw)

    async def review_cases(
        self,
        cases: list[GeneratedCase],
        feature_points: list[FeaturePoint],
        case_ids: list[int] | None = None,
    ) -> ReviewResponse:
        """用例质量评审：测试用例 + 功能点 → 综合评分 + 结构化建议"""

        # 序列化用例和功能点为 JSON
        cases_json = json.dumps(
            [
                {
                    "index": idx,
                    "title": c.title,
                    "priority": c.priority,
                    "steps": c.steps,
                    "expected": c.expected,
                    "script": c.script if c.script else "",
                }
                for idx, c in enumerate(cases)
            ],
            ensure_ascii=False,
            indent=2,
        )
        fp_json = json.dumps(
            [fp.model_dump() for fp in feature_points], ensure_ascii=False, indent=2
        )

        prompt = REVIEW_PROMPT.format(
            cases_json=cases_json,
            feature_points_json=fp_json,
        )

        raw = await self.chat(prompt)
        data = self._parse_json(raw)

        # 解析结构化建议
        suggestions = []
        for s in data.get("suggestions", []):
            case_index = s.get("case_index", 0)
            if case_index is None:
                case_index = 0
            # 通过 case_index 映射到真实 case_id
            mapped_case_id = None
            if case_ids and 0 <= case_index < len(case_ids):
                mapped_case_id = case_ids[case_index]

            # 过滤非法 field_path 值
            valid_fields = {"title", "precondition", "steps", "expected", "script"}
            field_path = [f for f in s.get("field_path", []) if f in valid_fields]

            suggestions.append(ReviewSuggestion(
                case_title=s.get("case_title", ""),
                case_index=case_index,
                case_id=mapped_case_id,
                field_path=field_path,
                issue_type=s.get("issue_type", "coverage_gap"),
                severity=s.get("severity", "medium"),
                problem=s.get("problem", s.get("issue", "")),
                issue=s.get("issue", s.get("problem", "")),
                suggestion=s.get("suggestion", ""),
                sample_patch=s.get("sample_patch"),
                example=s.get("example", ""),
            ))

        return ReviewResponse(
            overall_score=data.get("overall_score", 0),
            coverage_score=data.get("coverage_score", 0),
            completeness_score=data.get("completeness_score", 0),
            executability_score=data.get("executability_score", 0),
            suggestions=suggestions,
            summary=data.get("summary", ""),
            raw=raw,
        )

    async def review_single_case(
        self,
        case: GeneratedCase,
        feature_points: list[FeaturePoint],
        case_id: int | None = None,
    ) -> ReviewResponse:
        """单条用例评审：复用 review_cases，仅传入一条用例"""
        return await self.review_cases([case], feature_points, case_ids=[case_id] if case_id else None)

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
        if script.count("test(") < 1:
            errors.append("至少需要 1 个 test() 用例")
        if "expect(" not in script:
            errors.append("缺少 expect() 断言")

        forbidden = [
            (".css-", "禁止使用 CSS class hash 选择器"),
            ("nth-child", "禁止使用 nth-child 选择器"),
        ]
        for pattern, msg in forbidden:
            if pattern in script:
                errors.append(msg)

        if "waitForTimeout" in script:
            pass

        return errors

    @staticmethod
    def _parse_json(text: str) -> dict:
        """解析 AI 返回的 JSON"""
        if not text or not text.strip():
            raise RuntimeError("JSON 内容为空")
        
        text = text.strip()
        
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        
        text = text.replace('\r\n', '\n')
        
        text = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\u0075', text)
        
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            elif isinstance(parsed, list):
                return {"test_cases": parsed}
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON parse error (first attempt): {e}")
            print(f"[DEBUG] Error location: line {e.lineno}, column {e.colno}, pos {e.pos}")
            
            if e.lineno and e.colno:
                lines = text.split('\n')
                if e.lineno <= len(lines):
                    context_line = lines[e.lineno - 1]
                    print(f"[DEBUG] Context line {e.lineno}: {context_line}")
                    print(f"[DEBUG] Position: {' ' * (e.colno - 1)}^")
            pass
        
        def find_matching_brace(s, start_char, end_char):
            if not s.startswith(start_char):
                return None
            count = 1
            in_string = False
            escape = False
            for i, char in enumerate(s[1:], 1):
                if escape:
                    escape = False
                    continue
                if char == '\\':
                    escape = True
                    continue
                if char == '"':
                    in_string = not in_string
                    continue
                if not in_string:
                    if char == start_char:
                        count += 1
                    elif char == end_char:
                        count -= 1
                        if count == 0:
                            return s[:i+1]
            return None
        
        matched_json = find_matching_brace(text, '{', '}')
        if matched_json:
            try:
                parsed = json.loads(matched_json)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        
        matched_json = find_matching_brace(text, '[', ']')
        if matched_json:
            try:
                parsed = json.loads(matched_json)
                if isinstance(parsed, list):
                    return {"test_cases": parsed}
            except json.JSONDecodeError:
                pass
        
        json_match = re.search(r'(\{[\s\S]*\})', text)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        
        try:
            import ast
            parsed = ast.literal_eval(text)
            if isinstance(parsed, dict):
                return parsed
            elif isinstance(parsed, list):
                return {"test_cases": parsed}
        except (SyntaxError, ValueError):
            pass
        
        raise RuntimeError(f"JSON 解析失败\n原始内容前1000字符: {text[:1000]}\n原始内容后1000字符: {text[-1000:]}\n原始内容长度: {len(text)}")

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
        storage_state_path: str | None = None,
    ) -> RunResponse:
        """执行 Playwright 脚本并返回结果"""
        playwright_root = self.settings.playwright_root
        run_dir = self.settings.runtime_dir / uuid.uuid4().hex[:8]
        run_dir.mkdir(parents=True, exist_ok=True)
        spec_file = run_dir / "test.spec.ts"

        # 替换脚本中的 URL 占位（如果提供了 app_url）
        script_content = script
        if app_url:
            # 替换常见的 localhost 占位，以及 AI 生成的"未提供"占位符
            script_content = script_content.replace(
                "http://localhost:3000", app_url
            ).replace("http://localhost:8080", app_url
            ).replace("'未提供'", f"'{app_url}'"
            ).replace('"未提供"', f'"{app_url}"')

        spec_file.write_text(script_content, encoding="utf-8")

        # 从 Playwright 根目录执行，使用相对路径以便正确加载 node_modules
        spec_rel = spec_file.relative_to(playwright_root).as_posix()
        # 优先使用请求传入的 storage_state_path，其次使用配置文件中的
        effective_storage_state = storage_state_path or self.settings.storage_state_path
        cmd = self._build_command(spec_rel, run_dir, timeout, effective_storage_state)
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
                    # 对中文路径进行 URL 编码，避免 StaticFiles 404
                    encoded_path = quote(rel_path, safe='/')
                    screenshot_urls.append(f"/screenshots/{encoded_path}")
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
        self, spec_rel_path: str, work_dir: Path, timeout: int | None, storage_state_path: str | None = None
    ) -> list[str]:
        """构建 playwright test 命令"""
        npx = shutil.which("npx")
        if not npx:
            raise FileNotFoundError("npx")

        config_rel = Path(
            self._write_config(work_dir, storage_state_path)
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

    def _write_config(self, work_dir: Path, storage_state_path: str | None = None) -> str:
        """写入 playwright.config.ts（配置截图和浏览器）"""
        # Windows 路径反斜杠在 TS 字符串中会被当作转义符，需替换为正斜杠
        storage_state = storage_state_path.replace("\\", "/") if storage_state_path else None
        storage_line = f"storageState: '{storage_state}'," if storage_state else ""
        
        # 检查代理配置
        proxy_config = ""
        proxy_server = os.environ.get("PLAYWRIGHT_PROXY_SERVER")
        proxy_username = os.environ.get("PLAYWRIGHT_PROXY_USERNAME")
        proxy_password = os.environ.get("PLAYWRIGHT_PROXY_PASSWORD")
        if proxy_server:
            proxy_parts = [f"server: '{proxy_server}'"]
            if proxy_username:
                proxy_parts.append(f"username: '{proxy_username}'")
            if proxy_password:
                proxy_parts.append(f"password: '{proxy_password}'")
            proxy_config = f"\n    proxy: {{{', '.join(proxy_parts)}}},"
        
        config_content = f"""import {{ defineConfig }} from '@playwright/test';

export default defineConfig({{
  outputDir: '.test-results',
  use: {{
    browserName: '{self.settings.browser_type}',
    screenshot: 'on',
    video: 'retain-on-failure',
    {storage_line}{proxy_config}
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
        full_output = stderr + "\n" + stdout
        
        if "net::ERR_CONNECTION_RESET" in full_output:
            return "网络连接被重置。可能原因：\n1. 目标网站无法访问（网络限制/防火墙）\n2. 代理配置不正确\n3. 网站服务器拒绝连接\n\n解决方案：\n- 检查网络是否能访问目标URL\n- 如果需要代理，请设置环境变量 PLAYWRIGHT_PROXY_SERVER\n- 尝试使用其他网络环境"
        
        if "net::ERR_CONNECTION_REFUSED" in full_output:
            return "连接被拒绝。目标服务器未响应或端口未开放。"
        
        if "net::ERR_NAME_NOT_RESOLVED" in full_output:
            return "域名解析失败。请检查URL是否正确，或DNS配置是否正常。"
        
        if "net::ERR_TIMED_OUT" in full_output:
            return "连接超时。目标网站响应太慢或网络不稳定。"
        
        if "page.goto" in full_output and ("ERR_" in full_output or "Error:" in full_output):
            for line in full_output.splitlines():
                if "page.goto" in line or "Error:" in line:
                    return line[:500]
            return "页面导航失败，请检查目标URL是否可访问"
        
        for line in full_output.splitlines():
            line = line.strip()
            if line.startswith("Error:") or "error" in line.lower()[:20]:
                return line[:500]
        
        return stderr[-500:] if stderr else stdout[-500:]
