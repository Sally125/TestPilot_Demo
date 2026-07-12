"""一键流程演示脚本

验证核心链路：需求文本 → AI 分析 → 功能点 → Playwright 脚本生成 → 批量执行

使用方法：
    python run_demo.py

前置条件：
    1. 已在 .env 中配置 DEEPSEEK_API_KEY
    2. 已安装依赖：pip install -r requirements.txt
    3. 已配置 TEST_USERNAME / TEST_PASSWORD（登录成功用例需要）
"""

from __future__ import annotations

import asyncio
import datetime
import json
import re
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import get_settings
from app.models import GeneratedCase
from app.services import AIService, ExecutionService

# 示例需求文本（TodoMVC 待办事项应用）—— 使用 Playwright 官方 demo 网站
DEMO_REQUIREMENT = """
TodoMVC 待办事项应用测试需求：

1. 页面访问：URL 为 https://demo.playwright.dev/todomvc/，页面标题应包含"TodoMVC"
2. 输入框：页面顶部有一个输入框，placeholder为"What needs to be done?"，用于输入新待办事项
3. 添加待办：在输入框中输入内容后按 Enter 键，新待办事项应出现在列表中
4. 待办列表：显示所有待办事项，每个事项前有一个复选框
5. 完成待办：点击复选框，待办事项应显示为已完成状态（划线样式）
6. 删除待办：将鼠标悬停在待办事项上，应显示"×"删除按钮，点击后该事项被删除
7. 统计信息：页面底部显示待办事项数量统计（如"1 item left"）
8. 过滤功能：底部有三个过滤按钮（All、Active、Completed），点击可筛选不同状态的待办

被测应用地址：https://demo.playwright.dev/todomvc/
"""


def _module_filename(case: GeneratedCase, index: int) -> str:
    """按模块生成文件名"""
    module = case.module.strip() if case.module else f"module_{index:02d}"
    module = re.sub(r"[^\w\-]", "_", module)
    return f"{module}.spec.ts"


def _count_tests(script: str) -> int:
    """统计脚本中 test() 用例数量（不含 beforeEach）"""
    return len(re.findall(r"\btest\s*\(\s*['\"]", script))


def _save_scripts(
    cases: list[GeneratedCase], generated_dir: Path
) -> list[tuple[Path, GeneratedCase]]:
    """按模块保存脚本文件，返回 (路径, case) 列表"""
    saved: list[tuple[Path, GeneratedCase]] = []
    used_names: set[str] = set()

    for i, case in enumerate(cases, 1):
        filename = _module_filename(case, i)
        if filename in used_names:
            stem = Path(filename).stem
            filename = f"{stem}_{i}.spec.ts"
        used_names.add(filename)

        filepath = generated_dir / filename
        filepath.write_text(case.script, encoding="utf-8")
        saved.append((filepath, case))
        test_count = _count_tests(case.script)
        print(f"  → {filename} ({test_count} 个 test)")

    return saved


async def _batch_execute(
    saved: list[tuple[Path, GeneratedCase]],
    settings,
) -> dict:
    """批量执行所有生成的脚本，返回验收报告"""
    executor = ExecutionService(settings)
    results = []
    passed_count = 0

    for filepath, case in saved:
        print(f"\n执行: {filepath.name} — {case.title}")
        run_resp = await executor.run_script(
            case.script, app_url=settings.target_app_url
        )
        entry = {
            "file": filepath.name,
            "module": case.module,
            "title": case.title,
            "passed": run_resp.passed,
            "duration_ms": run_resp.duration_ms,
            "error": run_resp.error,
            "test_count": _count_tests(case.script),
        }
        results.append(entry)

        if run_resp.passed:
            passed_count += 1
            print(f"  ✓ 通过 ({run_resp.duration_ms}ms)")
        else:
            print(f"  ✗ 失败 ({run_resp.duration_ms}ms)")
            print(f"    错误: {run_resp.error}")

    total = len(results)
    return {
        "summary": {
            "total_modules": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "pass_rate": round(passed_count / total * 100, 1) if total else 0,
        },
        "results": results,
    }


async def main() -> None:
    settings = get_settings()

    print("=" * 70)
    print("TestPilot 核心链路演示")
    print("=" * 70)

    # 0. 前置检查
    if not settings.has_api_key:
        print("\n[错误] 未配置 DEEPSEEK_API_KEY")
        print("请执行：cp .env.example .env，然后填入你的 DeepSeek API Key")
        sys.exit(1)

    print(f"\n[配置] API Key: {settings.deepseek_api_key[:8]}...")
    print(f"[配置] 模型: {settings.deepseek_model}")
    print(f"[配置] 被测应用: {settings.target_app_url or '未配置'}")
    print(f"[配置] 测试账号: {settings.test_username or '未配置'}")

    ai = AIService(settings)

    # ===== 步骤 1：需求分析 =====
    print("\n" + "-" * 70)
    print("[步骤 1/3] 需求分析：需求文本 → 功能点列表")
    print("-" * 70)
    print(f"\n需求文本（节选）：{DEMO_REQUIREMENT.strip()[:80]}...")

    analyze_resp = await ai.analyze_requirement(
        DEMO_REQUIREMENT, app_url=settings.target_app_url
    )

    print(f"\n✓ 分析完成，提取 {len(analyze_resp.feature_points)} 个功能点：")
    for i, fp in enumerate(analyze_resp.feature_points, 1):
        print(f"  {i}. [{fp.priority}] {fp.name}")
        if fp.risk_hint:
            print(f"     ⚠ 风险: {fp.risk_hint}")

    print(f"\n摘要: {analyze_resp.summary}")
    print(f"预估用例数: {analyze_resp.estimated_case_count}")

    # ===== 步骤 2：脚本生成 =====
    print("\n" + "-" * 70)
    print("[步骤 2/3] 脚本生成：功能点 → Playwright 脚本（按模块分组）")
    print("-" * 70)

    generate_resp = await ai.generate_scripts(
        analyze_resp.feature_points, app_url=settings.target_app_url
    )

    total_tests = sum(_count_tests(c.script) for c in generate_resp.cases)
    print(f"\n✓ 生成完成，共 {len(generate_resp.cases)} 个模块 / {total_tests} 条用例：")
    for i, case in enumerate(generate_resp.cases, 1):
        test_count = _count_tests(case.script)
        has_describe = "test.describe" in case.script
        has_before = "test.beforeEach" in case.script
        struct = "✓" if has_describe and has_before else "✗"
        print(
            f"  {i}. [{case.priority}] {case.title} "
            f"({test_count} tests, 结构{struct}, 稳定性: {case.stability_score})"
        )

    # 检查脚本结构校验结果
    if generate_resp.raw and "validation_errors" in generate_resp.raw:
        print("\n⚠ 脚本结构校验未完全通过，详见 report.json")

    # 保存生成的脚本到文件（按时间创建子文件夹）
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    generated_dir = settings.generated_dir / timestamp
    generated_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[保存] 脚本文件保存到: {generated_dir}")
    saved = _save_scripts(generate_resp.cases, generated_dir)

    # ===== 步骤 3：批量执行 =====
    print("\n" + "-" * 70)
    print("[步骤 3/3] 脚本执行（批量验收所有模块）")
    print("-" * 70)

    if not saved:
        print("\n[跳过] 未生成任何用例")
        report = {"summary": {"total_modules": 0, "passed": 0, "failed": 0, "pass_rate": 0}, "results": []}
    else:
        report = await _batch_execute(saved, settings)

    report_path = generated_dir / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # ===== 验收报告 =====
    print("\n" + "-" * 70)
    print("[验收报告]")
    print("-" * 70)
    s = report["summary"]
    print(f"\n通过: {s['passed']}/{s['total_modules']} ({s['pass_rate']}%)")

    failed = [r for r in report["results"] if not r["passed"]]
    if failed:
        print("\n失败模块:")
        for r in failed:
            print(f"  - {r['file']}: {r['error']}")

    print(f"\n[报告] 已保存到: {report_path}")

    # ===== 总结 =====
    print("\n" + "=" * 70)
    print("演示完成")
    print("=" * 70)
    print("\n下一步：")
    print("  1. 检查 generated/ 目录下的模块脚本和 report.json")
    print("  2. 手动运行: npx playwright test <模块文件路径>")
    print("  3. 如果跑不通，调整 app/prompts.py 里的 GENERATE_PROMPT")
    print()


if __name__ == "__main__":
    asyncio.run(main())
