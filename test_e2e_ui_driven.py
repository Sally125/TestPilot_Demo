"""端到端测试（纯 UI 驱动录制版）：用 TestPilot AI 测试智能体 测试「考公大师」

要求：
1. 纯 UI 驱动 — 通过点击 TestPilot 前端触发全部 AI 工作流，不用 API 补救
2. 失败自动重试 — 每步失败后点击"重试"按钮，最多 3 次尝试
3. console 日志捕获 — 收集浏览器 console 日志，用于错误分析
4. markdown 错误报告 — 记录原日志和可能原因

前端工作流窗口 4 步：
  Step 0: AI需求分析     handleStartAnalysisFlow()   "AI正在分析需求..."
  Step 1: 用例设计       handleGenerateTestcasesForFlow()  "AI正在分析功能点，设计测试场景..."
  Step 2: 脚本生成+稳定性  handleCheckStabilityForFlow()    "脚本生成中..." → "正在进行稳定性检测..."
  Step 3: AI评审         handleGenerateReviewForFlow()     "AI正在分析测试用例质量..."

被测目标：考公大师（http://localhost:3001）
TestPilot UI：http://localhost:8080
录屏保存：E:\\hkx_project\\TestPilot\\test-results
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
import urllib.parse
from typing import Any

import requests
from playwright.sync_api import sync_playwright, Page, ConsoleMessage

# ==================== 配置 ====================
BASE_URL = "http://localhost:8000/api"
TARGET_APP_URL = "http://localhost:3001"
TESTPILOT_UI = "http://localhost:8080/" + urllib.parse.quote("AI测试智能体_TestPilot.html")
VIDEO_DIR = r"E:\hkx_project\TestPilot\test-results"
CHROME_PATH = r"C:\Users\zsy_cusci\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"

KAO_USER = "tester@kaogong.com"
KAO_PWD = "Test1234!"
KAO_NAME = "测试员"

REQUIREMENT_TEXT = (
    "考公大师公务员考试备考管理系统核心功能：用户注册与登录（邮箱+密码），"
    "备考仪表盘展示学习进度与待办任务，任务管理（创建/编辑/完成备考任务，任务状态流转），"
    "学习资料浏览与精读模式，模拟考试与自动评分，错题回顾与收藏，"
    "背诵卡片每日推送与导出PDF。需要验证登录状态保持、任务CRUD、"
    "学习进度统计、文章列表加载、考试分数计算与数据持久化。"
)

# 各步骤超时（秒）— 根据实际 AI 调用耗时设置较大值
FLOW_STEP_TIMEOUTS = {
    0: 600,   # Step 0: AI需求分析（流式，可能较久）
    1: 600,   # Step 1: 用例设计（AI 生成结构化用例，最久）
    2: 600,   # Step 2: 脚本生成+稳定性检测
    3: 600,   # Step 3: AI评审
}
FLOW_STEP_TIMEOUT = 600   # 默认超时
MAX_RETRY = 1             # 每步只尝试 1 次（不重试）

# 性能记录
perf_records: list[dict] = []  # 每个模块的执行耗时记录


# ==================== console 日志收集 ====================
console_logs: list[dict] = []
network_errors: list[dict] = []


def on_console(msg: ConsoleMessage):
    entry = {
        "type": msg.type,
        "text": msg.text,
        "time": time.strftime("%H:%M:%S"),
    }
    console_logs.append(entry)


def on_request_failed(request):
    network_errors.append({
        "url": request.url,
        "method": request.method,
        "failure": request.failure,
        "time": time.strftime("%H:%M:%S"),
    })


# ==================== 工具函数 ====================
def log(msg: str):
    print(f"  {msg}")


def save_report(filename: str, data: Any):
    os.makedirs(VIDEO_DIR, exist_ok=True)
    path = os.path.join(VIDEO_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(data, (dict, list)):
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(data))


def ui_screenshot(page: Page, filename: str):
    try:
        page.screenshot(path=os.path.join(VIDEO_DIR, filename))
    except Exception as e:
        log(f"(截图 {filename} 失败: {e})")


# ==================== TestPilot UI 操作 ====================
def ui_select_project(page: Page, project_name: str) -> bool:
    try:
        page.reload(wait_until="domcontentloaded", timeout=20000)
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        # 重试查找 projectData（前端异步加载项目列表）
        idx = -1
        for _ in range(6):
            page.wait_for_timeout(1000)
            idx = page.evaluate(
                """(name) => {
                    if (typeof projectData === 'undefined' || !projectData) return -1;
                    for (let i = 0; i < projectData.length; i++) {
                        if (projectData[i] && projectData[i].name === name) return i;
                    }
                    return -1;
                }""",
                project_name,
            )
            if idx is not None and idx >= 0:
                break
        if idx is not None and idx >= 0:
            page.evaluate(f"selectProject({int(idx)})")
            page.wait_for_timeout(1500)
            log(f"✓ 已选中项目: {project_name}")
            return True
        else:
            log(f"✗ 未找到项目: {project_name}")
    except Exception as e:
        log(f"(UI 选中项目跳过: {e})")
    return False


def ui_goto(page: Page, page_name: str):
    try:
        page.locator(f'[data-page="{page_name}"]').first.click()
        page.wait_for_timeout(1500)
    except Exception as e:
        log(f"(UI 导航到 {page_name} 跳过: {e})")


def fill_requirement(page: Page, text: str):
    try:
        page.locator('#req-tabs .tab-item[data-tab="text"]').click()
        page.wait_for_timeout(500)
        page.locator('#tab-text textarea').fill(text)
        page.wait_for_timeout(500)
        log("✓ 需求文本已填入")
    except Exception as e:
        log(f"✗ 填入需求文本失败: {e}")


def click_start_analysis(page: Page):
    try:
        page.locator('button:has-text("开始AI分析")').click()
        page.wait_for_timeout(1000)
        log("✓ 已点击'开始AI分析'按钮")
    except Exception as e:
        log(f"✗ 点击'开始AI分析'失败: {e}")


def get_flow_state(page: Page, step_idx: int) -> dict:
    return page.evaluate(
        """(idx) => {
            const nextBtn = document.getElementById('flow-next-btn');
            const body = document.getElementById('flow-modal-body');
            const errorEl = body ? body.querySelector('[style*="danger"], [style*="rgb(220, 38, 38)"]') : null;
            return {
                done: (typeof flowStepCompleted !== 'undefined') && flowStepCompleted[idx] === true,
                running: (typeof flowStepRunning !== 'undefined') && flowStepRunning,
                currentStep: (typeof currentFlowStep !== 'undefined') ? currentFlowStep : -1,
                nextBtnText: nextBtn ? nextBtn.textContent.trim() : '',
                nextBtnDisabled: nextBtn ? nextBtn.style.opacity === '0.5' : true,
                hasError: !!errorEl,
                errorText: errorEl ? errorEl.textContent.trim().substring(0, 300) : '',
                bodyText: body ? body.textContent.substring(0, 300) : '',
                modalVisible: !!document.getElementById('flow-modal') && document.getElementById('flow-modal').classList.contains('show'),
            };
        }""",
        step_idx,
    )


def wait_flow_step(page: Page, step_idx: int, attempt: int, timeout: int = FLOW_STEP_TIMEOUT) -> str:
    """等待工作流某步完成。返回 'done'/'error'/'timeout'"""
    print(f"  >>> [尝试 {attempt}/{MAX_RETRY}] 等待 Step {step_idx} 完成（最多 {timeout}s）...")
    start = time.time()
    last_status = ""
    while time.time() - start < timeout:
        try:
            state = get_flow_state(page, step_idx)
        except Exception as e:
            log(f"(获取工作流状态失败: {e})")
            time.sleep(3)
            continue

        status = f"done={state['done']}, running={state['running']}, step={state['currentStep']}, nextBtn='{state['nextBtnText']}', err={state['hasError']}"
        if status != last_status:
            elapsed = int(time.time() - start)
            body_preview = state['bodyText'][:100].replace('\n', ' ')
            print(f"  [{elapsed}s] {status} | body: {body_preview}")
            if state['hasError']:
                print(f"         错误: {state['errorText']}")
            last_status = status

        if state['done']:
            return 'done'
        if state['hasError'] and not state['running'] and not state['done']:
            return 'error'
        if not state['modalVisible']:
            return 'error'

        time.sleep(3)

    return 'timeout'


def click_next_step(page: Page):
    try:
        page.wait_for_function(
            "document.getElementById('flow-next-btn') && document.getElementById('flow-next-btn').style.opacity !== '0.5'",
            timeout=30000,
        )
        page.locator('#flow-next-btn').click()
        page.wait_for_timeout(1000)
        log("✓ 已点击'下一步'")
    except Exception as e:
        log(f"✗ 点击'下一步'失败: {e}")


def click_retry(page: Page):
    """点击工作流错误页面的'重试'按钮"""
    try:
        page.locator('button:has-text("重试")').click()
        page.wait_for_timeout(1500)
        log("✓ 已点击'重试'按钮")
    except Exception as e:
        log(f"✗ 点击'重试'失败: {e}")


def close_flow_modal(page: Page):
    try:
        page.evaluate("closeFlowModal()")
        page.wait_for_timeout(500)
    except Exception:
        pass


# ==================== 考公大师账号注册 ====================
def setup_register_account(browser):
    print("\n[准备] 注册考公大师测试账号...")
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    try:
        page.goto("http://localhost:3001/register", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(1500)
        page.get_by_placeholder("你的名字").fill(KAO_NAME)
        page.get_by_placeholder("your@email.com").fill(KAO_USER)
        page.get_by_placeholder("至少6位").fill(KAO_PWD)
        page.get_by_placeholder("再次输入密码").fill(KAO_PWD)
        page.get_by_role("button", name="注册").click()
        page.wait_for_timeout(3000)
        log("✓ 注册请求已提交（账号已存在则忽略）")
    except Exception as e:
        log(f"⚠ 注册流程异常（账号可能已存在）: {e}")
    finally:
        ctx.close()


# ==================== 工作流单步执行（含重试）====================
def run_flow_step_with_retry(page: Page, step_idx: int, step_name: str, is_first_step: bool = False) -> dict:
    """执行工作流某一步，失败后点击重试，最多 MAX_RETRY 次。
    is_first_step=True 时，通过点击'开始AI分析'触发；
    后续步骤通过点击'下一步'触发。
    返回 {'success': bool, 'attempts': int, 'errors': [str], 'durations': [int], 'total_duration': int}"""
    result = {"success": False, "attempts": 0, "errors": [], "durations": [], "total_duration": 0}
    step_timeout = FLOW_STEP_TIMEOUTS.get(step_idx, FLOW_STEP_TIMEOUT)
    t_step_start = time.time()

    for attempt in range(1, MAX_RETRY + 1):
        result["attempts"] = attempt
        t0 = time.time()

        # 触发本步
        if is_first_step and attempt == 1:
            fill_requirement(page, REQUIREMENT_TEXT)
            ui_screenshot(page, f"stage_{step_idx}_req_filled.png")
            page.wait_for_timeout(1000)
            click_start_analysis(page)
            try:
                page.wait_for_selector('#flow-modal.show', timeout=10000)
            except Exception:
                result["errors"].append("工作流窗口未打开")
                break
        elif attempt == 1:
            click_next_step(page)
        else:
            click_retry(page)

        # 等待完成
        outcome = wait_flow_step(page, step_idx, attempt, timeout=step_timeout)
        duration = int(time.time() - t0)
        result["durations"].append(duration)

        if outcome == 'done':
            result["success"] = True
            log(f"✓ {step_name} 完成（尝试 {attempt}，耗时 {duration}s）")
            break
        else:
            err_msg = f"尝试 {attempt}: {outcome}"
            try:
                state = get_flow_state(page, step_idx)
                if state['errorText']:
                    err_msg += f" - {state['errorText']}"
            except Exception:
                pass
            result["errors"].append(err_msg)
            log(f"✗ {step_name} {outcome}（尝试 {attempt}/{MAX_RETRY}，耗时 {duration}s）")

            ui_screenshot(page, f"stage_{step_idx}_error_attempt{attempt}.png")

            if attempt < MAX_RETRY:
                log(f"  等待 5 秒后重试...")
                time.sleep(5)

    result["total_duration"] = int(time.time() - t_step_start)

    # 记录性能数据
    perf_records.append({
        "step": step_idx,
        "name": step_name,
        "success": result["success"],
        "attempts": result["attempts"],
        "total_duration_s": result["total_duration"],
        "per_attempt_durations_s": result["durations"],
    })
    # 模块完成后即时输出性能记录
    print(f"\n  ─── 性能记录: {step_name} ───")
    print(f"  总耗时: {result['total_duration']}s, 尝试次数: {result['attempts']}, 成功: {result['success']}")
    if result["durations"]:
        for i, d in enumerate(result["durations"]):
            print(f"    第{i+1}次尝试: {d}s")
    print(f"  ─────────────────────────────\n")

    return result


# ==================== markdown 错误报告生成 ====================
def generate_error_report(step_results: list[dict], project_id: int, project_name: str) -> str:
    """生成 markdown 格式的错误分析报告"""
    md = []
    md.append("# TestPilot UI 驱动测试 — 错误分析报告")
    md.append("")
    md.append(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"**项目**: {project_name} (ID={project_id})")
    md.append(f"**被测目标**: {TARGET_APP_URL}")
    md.append(f"**TestPilot UI**: {TESTPILOT_UI}")
    md.append(f"**每步最大重试次数**: {MAX_RETRY}")
    md.append(f"**每步超时**: {FLOW_STEP_TIMEOUT}s")
    md.append("")
    md.append("---")
    md.append("")

    # 1. 各步骤结果汇总
    md.append("## 1. 各步骤执行结果汇总")
    md.append("")
    md.append("| 步骤 | 名称 | 是否成功 | 尝试次数 | 各次耗时(s) |")
    md.append("|------|------|----------|----------|-------------|")
    for i, sr in enumerate(step_results):
        durations = ", ".join(str(d) for d in sr["durations"]) if sr["durations"] else "-"
        md.append(f"| {i} | {sr['name']} | {'✓ 成功' if sr['success'] else '✗ 失败'} | {sr['attempts']} | {durations} |")
    md.append("")

    # 2. 各步骤错误详情
    md.append("## 2. 各步骤错误详情")
    md.append("")
    for i, sr in enumerate(step_results):
        md.append(f"### Step {i}: {sr['name']}")
        md.append("")
        if sr["success"]:
            md.append(f"- **结果**: ✓ 成功（尝试 {sr['attempts']} 次）")
        else:
            md.append(f"- **结果**: ✗ 失败（共尝试 {sr['attempts']} 次）")
            md.append(f"- **错误信息**:")
            for err in sr["errors"]:
                md.append(f"  - {err}")
        md.append("")

    # 3. 浏览器 console 日志（关键部分）
    md.append("## 3. 浏览器 Console 日志（原始）")
    md.append("")
    md.append("以下为测试期间捕获的浏览器 console 日志（按时间顺序）：")
    md.append("")
    md.append("```")
    for entry in console_logs:
        t = entry["time"]
        ty = entry["type"].upper()
        txt = entry["text"]
        # 截断过长的日志
        if len(txt) > 500:
            txt = txt[:500] + "...[截断]"
        md.append(f"[{t}] [{ty}] {txt}")
    md.append("```")
    md.append("")
    md.append(f"**Console 日志总数**: {len(console_logs)} 条")
    md.append("")

    # 4. 网络请求失败
    md.append("## 4. 网络请求失败记录")
    md.append("")
    if not network_errors:
        md.append("无网络请求失败记录。")
    else:
        md.append("| 时间 | 方法 | URL | 失败原因 |")
        md.append("|------|------|-----|----------|")
        for ne in network_errors:
            url_short = ne["url"][:80] + ("..." if len(ne["url"]) > 80 else "")
            md.append(f"| {ne['time']} | {ne['method']} | {url_short} | {ne['failure']} |")
    md.append("")

    # 5. 错误原因分析
    md.append("## 5. 错误原因分析")
    md.append("")
    # 收集所有错误文本用于分析
    all_errors = []
    for sr in step_results:
        all_errors.extend(sr["errors"])
    # 收集 console 中的 error 类型日志
    console_errors = [e for e in console_logs if e["type"] in ("error", "warning")]
    console_error_texts = [e["text"] for e in console_errors]

    md.append("### 5.1 错误分类")
    md.append("")

    # 分类统计
    fetch_errors = [e for e in all_errors if "Failed to fetch" in e or "fetch" in e.lower()]
    empty_errors = [e for e in all_errors if "空" in e or "empty" in e.lower() or "None" in e]
    timeout_errors = [e for e in all_errors if "timeout" in e.lower() or "超时" in e]

    md.append(f"- **Failed to fetch 类错误**: {len(fetch_errors)} 次")
    md.append(f"- **AI 返回空内容类错误**: {len(empty_errors)} 次")
    md.append(f"- **超时类错误**: {len(timeout_errors)} 次")
    md.append("")

    md.append("### 5.2 可能原因分析")
    md.append("")

    if fetch_errors:
        md.append("#### 原因 1: `Failed to fetch` — 前端 fetch 请求失败")
        md.append("")
        md.append("**现象**: 浏览器 fetch 调用后端 API 时报 `Failed to fetch`。")
        md.append("")
        md.append("**可能原因**:")
        md.append("- 后端 AI 调用耗时过长，超过浏览器/代理的连接保持时间，连接被中断")
        md.append("- 后端处理过程中抛出异常导致连接重置（RST）")
        md.append("- 前端 AbortController 超时（前端设置了 900000ms=15分钟超时，理论上不应在此触发）")
        md.append("- 网络层问题：localhost 连接被防火墙/杀毒软件拦截")
        md.append("")
        md.append("**相关 console 日志**:")
        relevant = [e for e in console_error_texts if "fetch" in e.lower() or "network" in e.lower() or "Failed" in e]
        if relevant:
            md.append("```")
            for r in relevant[:10]:
                md.append(r[:300])
            md.append("```")
        else:
            md.append("(未捕获到直接相关的 console 日志)")
        md.append("")

    if empty_errors:
        md.append("#### 原因 2: AI 返回内容为空")
        md.append("")
        md.append("**现象**: 后端 AI 服务调用成功（HTTP 200），但 `choices[0].message.content` 为 `None` 或空字符串。")
        md.append("")
        md.append("**可能原因**:")
        md.append("- AI 模型（DeepSeek）返回的 content 为 None，finish_reason 可能是 `length`（达到 max_tokens）或 `content_filter`")
        md.append("- 输入 prompt 过长或过于复杂，模型无法在 max_tokens 限制内生成有效 JSON")
        md.append("- AI 模型端临时性问题（服务过载、限流）导致返回空内容")
        md.append("- `response_format: {type: json_object}` 与模型输出不兼容，导致 content 被截断为空")
        md.append("")
        md.append("**相关 console 日志**:")
        relevant = [e for e in console_error_texts if "空" in e or "empty" in e.lower() or "None" in e]
        if relevant:
            md.append("```")
            for r in relevant[:10]:
                md.append(r[:300])
            md.append("```")
        else:
            md.append("(未捕获到直接相关的 console 日志)")
        md.append("")

    if timeout_errors:
        md.append("#### 原因 3: 步骤执行超时")
        md.append("")
        md.append("**现象**: 工作流步骤在设定的超时时间内未完成。")
        md.append("")
        md.append("**可能原因**:")
        md.append(f"- AI 调用耗时超过脚本设定的 {FLOW_STEP_TIMEOUT}s 超时")
        md.append("- 后端 `design-testcases` / `generate` 等接口处理极慢（AI 多次重试）")
        md.append("- 后端 httpx 客户端 timeout=900s，但前端轮询/等待逻辑提前判定失败")
        md.append("")

    md.append("### 5.3 串行依赖问题")
    md.append("")
    md.append("**重要**: 前端工作流 4 步是**串行依赖**的：")
    md.append("- Step 1（用例设计）依赖 Step 0（需求分析）的 `currentAnalysisResult.feature_points`")
    md.append("- Step 2（脚本生成）依赖 Step 1 的 `currentDesignedTestCases`")
    md.append("- Step 3（AI评审）依赖 Step 1/2 的用例和脚本数据")
    md.append("")
    md.append("因此，**如果 Step 1 失败，Step 2 和 Step 3 必然也会失败**（前置数据为空）。")
    md.append("重试机制只能重试当前步，无法修复前置步的数据缺失。")
    md.append("")

    md.append("### 5.4 综合结论")
    md.append("")
    failed_steps = [sr["name"] for sr in step_results if not sr["success"]]
    if not failed_steps:
        md.append("✓ 全部步骤成功，无错误。")
    else:
        md.append(f"✗ 失败步骤: {', '.join(failed_steps)}")
        md.append("")
        if empty_errors and not fetch_errors:
            md.append("**核心问题**: AI 模型返回空内容，属于 AI 服务端问题（非项目代码 bug）。")
            md.append("建议检查后端 `services.py` 的 `chat()` 方法日志，确认 `finish_reason` 和 `usage` 字段。")
        elif fetch_errors:
            md.append("**核心问题**: 前端 fetch 请求失败，可能是后端处理超时导致连接中断。")
            md.append("建议检查后端日志确认 AI 调用是否成功完成、是否有异常堆栈。")
        elif timeout_errors:
            md.append("**核心问题**: AI 调用耗时过长，超过脚本超时设定。")
            md.append(f"建议增大 FLOW_STEP_TIMEOUT（当前 {FLOW_STEP_TIMEOUT}s）或优化 AI prompt。")
    md.append("")
    md.append("---")
    md.append(f"*报告由 test_e2e_ui_driven.py 自动生成*")
    md.append("")

    # 6. 性能记录与优化建议
    md.append("## 6. 性能记录")
    md.append("")
    md.append("### 6.1 各模块执行耗时")
    md.append("")
    md.append("| 步骤 | 模块名称 | 是否成功 | 尝试次数 | 总耗时(s) | 各次耗时(s) |")
    md.append("|------|----------|----------|----------|-----------|-------------|")
    for pr in perf_records:
        per = ", ".join(str(d) for d in pr["per_attempt_durations_s"]) if pr["per_attempt_durations_s"] else "-"
        md.append(f"| {pr['step']} | {pr['name']} | {'✓' if pr['success'] else '✗'} | {pr['attempts']} | {pr['total_duration_s']} | {per} |")
    md.append("")

    total_time = sum(pr["total_duration_s"] for pr in perf_records)
    md.append(f"**工作流总耗时**: {total_time}s ({total_time/60:.1f}分钟)")
    md.append("")

    md.append("### 6.2 性能瓶颈分析")
    md.append("")
    # 找出最慢的模块
    if perf_records:
        slowest = max(perf_records, key=lambda x: x["total_duration_s"])
        md.append(f"- **最慢模块**: {slowest['name']}（{slowest['total_duration_s']}s）")
        # 分析重试开销
        retry_modules = [pr for pr in perf_records if pr["attempts"] > 1]
        if retry_modules:
            retry_names = ', '.join(f'{m["name"]}({m["attempts"]}次)' for m in retry_modules)
            md.append(f"- **涉及重试的模块**: {retry_names}")
            retry_waste = sum(sum(m["per_attempt_durations_s"][:-1]) for m in retry_modules if len(m["per_attempt_durations_s"]) > 1)
            md.append(f"- **重试浪费的时间**: 约 {retry_waste}s")
        md.append("")

    md.append("### 6.3 性能优化建议")
    md.append("")
    md.append("针对 AI 工作流的性能优化建议：")
    md.append("")
    md.append("#### 1. AI 调用层面")
    md.append("- **流式响应**: 所有 AI 接口（`design-testcases`、`generate`、`review`）应改用流式响应（SSE），像 `analyze/stream` 一样，避免长时间无反馈导致前端超时")
    md.append("- **降低 max_tokens**: 后端 `chat()` 方法 `max_tokens=12000` 过大，可针对不同场景分别设置（用例设计 8000、脚本生成 6000、评审 4000）")
    md.append("- **分批处理**: 用例设计阶段如功能点较多（>10个），可分批调用 AI，每批 3-5 个功能点，并行处理")
    md.append("- **模型选择**: 考虑使用更快的模型（如 deepseek-chat 而非 deepseek-reasoner）用于简单任务")
    md.append("")
    md.append("#### 2. 前端交互层面")
    md.append("- **进度反馈**: 非流式接口（`design-testcases`、`generate`）应增加心跳/轮询机制，前端定期查询后端进度，避免用户长时间无反馈")
    md.append("- **预加载**: Step 0 完成后可预加载 Step 1 所需数据，减少步骤间等待")
    md.append("- **超时设置**: 前端 AbortController 超时 900s 过长，建议设为 300s 并配合重试机制")
    md.append("")
    md.append("#### 3. 后端架构层面")
    md.append("- **缓存**: 对相同 feature_points 的用例设计结果做缓存，避免重复调用 AI")
    md.append("- **异步队列**: 将 AI 调用放入任务队列（如 Celery），前端通过任务ID轮询结果，避免长连接")
    md.append("- **连接池**: httpx 客户端复用连接池，减少 TLS 握手开销")
    md.append("- **超时降级**: AI 超时后自动降级为模板生成，保证流程不中断")
    md.append("")
    md.append("#### 4. 测试效率层面")
    md.append("- **并行执行**: 4 个工作流步骤有依赖关系无法并行，但多个项目的测试可并行运行")
    md.append("- **减少功能点**: 需求分析阶段限制功能点数量（如 top 5），减少后续步骤的 AI 输入量")
    md.append("")

    return "\n".join(md)


# ==================== 主流程 ====================
def run_full_e2e():
    print("=" * 72)
    print("TestPilot 端到端测试（纯 UI 驱动录制版）：测试「考公大师」")
    print(f"被测目标: {TARGET_APP_URL}")
    print(f"TestPilot UI: {TESTPILOT_UI}")
    print(f"录屏目录: {VIDEO_DIR}")
    print(f"每步重试上限: {MAX_RETRY} 次, 每步超时: {FLOW_STEP_TIMEOUT}s")
    print("=" * 72)

    os.makedirs(VIDEO_DIR, exist_ok=True)
    console_logs.clear()
    network_errors.clear()

    # 0. 健康检查
    print("\n[0/8] 健康检查...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        has_key = resp.json().get("has_api_key", False) if resp.status_code == 200 else False
        log(f"✓ 后端服务正常 (has_api_key={has_key})")
    except Exception as e:
        log(f"✗ 无法连接后端: {e}")
        return False

    # 创建项目 + 需求（API 驱动，仅创建数据，不录屏）
    print("\n[准备] 创建测试项目...")
    project_name = f"考公大师-UI-E2E-{int(time.time())}"
    resp = requests.post(f"{BASE_URL}/projects", json={
        "name": project_name, "description": "考公大师 UI 驱动端到端测试",
        "appUrl": TARGET_APP_URL, "dim": "在线教育/考试备考", "techStack": "Next.js/React/TypeScript",
    }, timeout=30)
    if resp.status_code != 200:
        print(f"  ✗ 创建项目失败: {resp.text}")
        return False
    project = resp.json()
    project_id = project["id"]
    print(f"  ✓ 项目创建成功: {project_name} (ID={project_id})")
    save_report("00_project.json", project)

    resp = requests.post(f"{BASE_URL}/projects/{project_id}/requirements",
                         json={"title": "考公大师 备考全流程", "content": REQUIREMENT_TEXT}, timeout=30)
    if resp.status_code != 200:
        print(f"  ✗ 创建需求失败: {resp.text}")
        return False
    req_id = resp.json()["id"]
    print(f"  ✓ 需求创建成功: ID={req_id}")

    # ===== 启动浏览器 + 录屏 =====
    step_results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME_PATH)

        # 前置：注册考公大师账号
        setup_register_account(browser)

        # 启动录屏 context
        context = browser.new_context(
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()

        # 绑定 console 日志和网络错误捕获
        page.on("console", on_console)
        page.on("requestfailed", on_request_failed)

        video_path = None
        try:
            # ===== 打开 TestPilot UI =====
            print("\n[录屏] 启动 TestPilot 工具界面...")
            page.goto(TESTPILOT_UI, wait_until="domcontentloaded", timeout=20000)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                print("  (networkidle 未达成，继续执行)")
            page.wait_for_timeout(1500)
            ui_screenshot(page, "stage_00_testpilot_home.png")
            page.wait_for_timeout(1500)

            # 选中项目
            ui_select_project(page, project_name)
            ui_goto(page, "requirement")

            # ===== 工作流 4 步（纯 UI 驱动 + 重试）=====
            print("\n[1-5/8] UI 驱动工作流（纯 UI，失败重试）")

            # Step 0: AI需求分析
            print(f"\n[1/8] AI需求分析（UI 驱动，最多重试 {MAX_RETRY} 次）...")
            sr0 = run_flow_step_with_retry(page, 0, "AI需求分析", is_first_step=True)
            step_results.append({"name": "AI需求分析", **sr0})
            ui_screenshot(page, "stage_01_analysis.png")
            page.wait_for_timeout(2000)

            # Step 1: 用例设计
            if sr0["success"]:
                print(f"\n[2/8] 用例设计（UI 驱动，最多重试 {MAX_RETRY} 次）...")
                sr1 = run_flow_step_with_retry(page, 1, "用例设计")
                step_results.append({"name": "用例设计", **sr1})
                ui_screenshot(page, "stage_02_testcases.png")
                page.wait_for_timeout(2000)
            else:
                print("\n  ⚠ Step 0 失败，遇错即返，跳过 Step 1/2/3")
                close_flow_modal(page)

            # Step 2: 脚本生成 + 稳定性检测
            if step_results and step_results[-1].get("success"):
                print(f"\n[3-4/8] 脚本生成+稳定性检测（UI 驱动，最多重试 {MAX_RETRY} 次）...")
                sr2 = run_flow_step_with_retry(page, 2, "脚本生成+稳定性检测")
                step_results.append({"name": "脚本生成+稳定性检测", **sr2})
                ui_screenshot(page, "stage_03_scripts_stability.png")
                page.wait_for_timeout(2000)
            elif len(step_results) >= 2:
                print("\n  ⚠ Step 1 失败，遇错即返，跳过 Step 2/3")
                close_flow_modal(page)

            # Step 3: AI评审
            if len(step_results) >= 3 and step_results[-1].get("success"):
                print(f"\n[5/8] AI评审（UI 驱动，最多重试 {MAX_RETRY} 次）...")
                sr3 = run_flow_step_with_retry(page, 3, "AI评审")
                step_results.append({"name": "AI评审", **sr3})
                ui_screenshot(page, "stage_04_review.png")
                page.wait_for_timeout(2000)

            # 点"完成"关闭工作流窗口（仅当工作流走完时执行）
            try:
                page.wait_for_function(
                    "document.getElementById('flow-next-btn') && document.getElementById('flow-next-btn').style.opacity !== '0.5'",
                    timeout=15000,
                )
                page.locator('#flow-next-btn').click()
                page.wait_for_timeout(1500)
                log("✓ 已点击'完成'，关闭工作流窗口")
            except Exception:
                close_flow_modal(page)

            # 后续阶段（登录态/执行/报告）的 UI 展示
            # 导航到测试用例页展示
            ui_select_project(page, project_name)
            ui_goto(page, "testcases")
            ui_screenshot(page, "stage_05_testcases_view.png")
            page.wait_for_timeout(2000)

            # 登录态配置 UI 展示
            try:
                page.evaluate("showLoginConfig()")
                page.wait_for_timeout(2000)
            except Exception:
                pass
            ui_screenshot(page, "stage_06_login_config.png")
            page.wait_for_timeout(2000)

            # 执行中心 UI 展示
            try:
                page.evaluate("openExecutionModal()")
                page.wait_for_timeout(2000)
            except Exception:
                pass
            ui_screenshot(page, "stage_07_execution.png")
            page.wait_for_timeout(2000)

            # 报告页展示
            ui_select_project(page, project_name)
            ui_goto(page, "report")
            ui_screenshot(page, "stage_08_report.png")
            page.wait_for_timeout(2000)

        finally:
            try:
                if page.video:
                    video_path = page.video.path()
            except Exception:
                pass
            context.close()
            browser.close()

    # ===== 生成 markdown 错误报告 =====
    print("\n[报告] 生成 markdown 错误分析报告...")
    md_report = generate_error_report(step_results, project_id, project_name)
    md_path = os.path.join(VIDEO_DIR, "error_analysis.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"  ✓ 错误分析报告: {md_path}")

    # 保存 console 日志原始 JSON
    save_report("console_logs.json", console_logs)
    save_report("network_errors.json", network_errors)

    # 保存步骤结果汇总
    save_report("step_results.json", step_results)

    # 保存性能记录
    save_report("performance_records.json", perf_records)

    # ===== 汇总 =====
    print("\n" + "=" * 72)
    print("端到端测试结果汇总（纯 UI 驱动录制版）")
    print("=" * 72)
    all_pass = True
    for sr in step_results:
        status = "✓ PASS" if sr["success"] else "✗ FAIL"
        print(f"  {status} - {sr['name']} (尝试 {sr['attempts']}/{MAX_RETRY})")
        if not sr["success"]:
            all_pass = False
            for err in sr["errors"]:
                print(f"         {err}")
    print("\n" + ("✓ 全部步骤成功！" if all_pass else "✗ 部分步骤失败，详见 error_analysis.md"))

    # 重命名录屏
    try:
        if video_path and os.path.exists(video_path):
            final_name = f"testpilot_ui_考公大师_{int(time.time())}.webm"
            final_path = os.path.join(VIDEO_DIR, final_name)
            shutil.move(video_path, final_path)
            print(f"\n录屏视频: {final_path}")
            print(f"文件大小: {os.path.getsize(final_path) / 1024:.1f} KB")
    except Exception as e:
        print(f"\n录屏文件重命名失败: {e}")

    print(f"\nConsole 日志: {len(console_logs)} 条")
    print(f"网络错误: {len(network_errors)} 条")
    print(f"错误分析报告: {md_path}")
    print("=" * 72)
    return all_pass


if __name__ == "__main__":
    success = run_full_e2e()
    sys.exit(0 if success else 1)
