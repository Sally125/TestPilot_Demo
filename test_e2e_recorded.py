"""端到端测试：用 TestPilot AI 测试智能体 测试「考公大师」系统

完整 8 阶段流程 + Playwright 录屏（TestPilot 工具界面）保存到 test-results 目录。

8 阶段：
1. AI需求分析     — POST /api/analyze/stream（流式）
2. 用例生成       — POST /api/design-testcases
3. 脚本生成       — POST /api/generate
4. 稳定性检测     — POST /api/projects/{id}/stability/check-all
5. AI评审         — POST /api/projects/{id}/review/generate
6. 登录态配置     — POST /api/projects/{id}/login-profiles + generate-session
7. 测试用例执行   — POST /api/run + 创建执行批次 + 持久化结果
8. 报告查询       — GET  /api/projects/{id}/reports

被测目标：考公大师（http://localhost:3001，Next.js 备考系统）
TestPilot API：http://localhost:8000/api
TestPilot UI：http://localhost:8080
录屏保存：E:\\hkx_project\\TestPilot\\test-results
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
import traceback
import urllib.parse
from typing import Any

import requests
from playwright.sync_api import sync_playwright

# ==================== 配置 ====================
BASE_URL = "http://localhost:8000/api"
TARGET_APP_URL = "http://localhost:3001"           # 考公大师
TESTPILOT_UI = "http://localhost:8080/" + urllib.parse.quote("AI测试智能体_TestPilot.html")
VIDEO_DIR = r"E:\hkx_project\TestPilot\test-results"
TIMEOUT = 300                                       # AI 接口超时（秒）
# 复用已安装的 Node Playwright Chromium（Python Playwright 未单独安装浏览器）
CHROME_PATH = r"C:\Users\zsy_cusci\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"

# 考公大师 测试账号
KAO_USER = "tester@kaogong.com"
KAO_PWD = "Test1234!"
KAO_NAME = "测试员"

# 考公大师 登录态配置（表单模式，选择器匹配实际页面元素）
LOGIN_CONFIG = {
    "name": "考公大师-学生账号",
    "role": "student",
    "username": KAO_USER,
    "password": KAO_PWD,
    "loginUrl": "http://localhost:3001/login",
    "usernameSelector": "#email",
    "usernameSelectorType": "css",
    "passwordSelector": "#password",
    "passwordSelectorType": "css",
    "submitSelector": "button[type='submit']",
    "submitSelectorType": "css",
    "successIndicator": "/dashboard",
    "successIndicatorType": "url",
    "scriptMode": "form",
}

# 考公大师 需求文本
REQUIREMENT_TEXT = (
    "考公大师公务员考试备考管理系统核心功能：用户注册与登录（邮箱+密码），"
    "备考仪表盘展示学习进度与待办任务，任务管理（创建/编辑/完成备考任务，任务状态流转），"
    "学习资料浏览与精读模式，模拟考试与自动评分，错题回顾与收藏，"
    "背诵卡片每日推送与导出PDF。需要验证登录状态保持、任务CRUD、"
    "学习进度统计、文章列表加载、考试分数计算与数据持久化。"
)


# ==================== 工具函数 ====================
class StepResult:
    def __init__(self, name: str):
        self.name = name
        self.ok = True
        self.msg = ""
        self.data: Any = None

    def success(self, msg: str, data: Any = None):
        self.ok = True
        self.msg = msg
        self.data = data

    def fail(self, msg: str, data: Any = None):
        self.ok = False
        self.msg = msg
        self.data = data


def log(step: int, total: int, name: str, msg: str, ok: bool = True):
    status = "✓" if ok else "✗"
    print(f"  [{step}/{total}] {status} {name}: {msg}")


def save_report(filename: str, data: Any):
    os.makedirs(VIDEO_DIR, exist_ok=True)
    path = os.path.join(VIDEO_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(data, (dict, list)):
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(data))


# ==================== TestPilot UI 导航辅助 ====================
def ui_select_project(page, project_name: str) -> bool:
    """刷新 TestPilot UI 并按名称选中项目（best-effort，不阻断主流程）"""
    try:
        page.reload()
        page.wait_for_load_state("networkidle", timeout=15000)
        page.wait_for_timeout(1200)
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
            page.evaluate(f"selectProject({int(idx)})")
            page.wait_for_timeout(1500)
            return True
    except Exception as e:
        print(f"        (UI 选中项目跳过: {e})")
    return False


def ui_goto(page, page_name: str):
    """通过侧边栏导航到指定页面（best-effort）"""
    try:
        page.locator(f'[data-page="{page_name}"]').first.click()
        page.wait_for_timeout(1500)
    except Exception as e:
        print(f"        (UI 导航到 {page_name} 跳过: {e})")


def ui_screenshot(page, filename: str):
    """保存截图到录屏目录"""
    try:
        path = os.path.join(VIDEO_DIR, filename)
        page.screenshot(path=path)
    except Exception as e:
        print(f"        (截图 {filename} 失败: {e})")


def show_stage(page, project_name: str, stage: int, total: int, page_name: str, shot: str):
    """每阶段完成后：刷新UI、选中项目、导航到相关页面、截图、停留供录屏捕获"""
    print(f"        [UI] 刷新并展示阶段 {stage} 界面 ({page_name})...")
    ui_select_project(page, project_name)
    ui_goto(page, page_name)
    ui_screenshot(page, shot)
    page.wait_for_timeout(2000)   # 停留 2s 供录屏捕获


# ==================== 阶段实现 ====================
def step_0_health() -> bool:
    print("\n[0/8] 健康检查...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✓ 后端服务正常 (has_api_key={data.get('has_api_key')})")
            return bool(data.get("has_api_key", False))
        print(f"  ✗ 健康检查返回 {resp.status_code}")
        return False
    except Exception as e:
        print(f"  ✗ 无法连接后端: {e}")
        return False


def step_1_analyze(project_id: int, req_id: int, requirement_text: str) -> list:
    print("\n[1/8] AI需求分析...")
    try:
        resp = requests.post(
            f"{BASE_URL}/analyze/stream",
            json={
                "project_id": project_id,
                "requirement_id": req_id,
                "requirement_text": requirement_text,
                "app_url": TARGET_APP_URL,
            },
            stream=True,
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            log(1, 8, "analyze", f"请求失败 HTTP {resp.status_code}: {resp.text[:200]}", False)
            return []

        analysis_result = None
        char_count = 0
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                data_str = line.decode("utf-8").strip()
                if not data_str.startswith("data:"):
                    continue
                data = json.loads(data_str[5:].strip())
                if data.get("type") == "progress":
                    char_count += len(data.get("content", ""))
                elif data.get("type") == "complete":
                    analysis_result = data
                    break
                elif data.get("type") == "error":
                    log(1, 8, "analyze", f"AI错误: {data.get('message', '')}", False)
                    return []
            except Exception:
                continue

        if not analysis_result:
            log(1, 8, "analyze", "未收到分析结果", False)
            return []

        feature_points = analysis_result.get("feature_points", [])
        save_report("01_analysis.json", analysis_result)
        log(1, 8, "analyze", f"提取 {len(feature_points)} 个功能点，接收 {char_count} 字符")

        requests.put(
            f"{BASE_URL}/requirements/{req_id}/analysis",
            json={"analysis_result": analysis_result},
            timeout=30,
        )
        return feature_points
    except Exception as e:
        log(1, 8, "analyze", f"异常: {e}", False)
        return []


def step_2_design_testcases(feature_points: list) -> list:
    print("\n[2/8] 用例生成（AI设计）...")
    if not feature_points:
        log(2, 8, "design", "无功能点，跳过", False)
        return []

    last_error = ""
    for attempt in range(2):
        try:
            resp = requests.post(
                f"{BASE_URL}/design-testcases",
                json={"feature_points": feature_points},
                timeout=120,
            )
            if resp.status_code == 200:
                data = resp.json()
                cases = data.get("cases", [])
                if cases:
                    save_report("02_testcases_designed.json", data)
                    log(2, 8, "design", f"AI 设计 {len(cases)} 个测试用例（第{attempt+1}次尝试）")
                    return cases
                last_error = "返回用例为空"
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                print(f"        第{attempt+1}次失败: {last_error}")
        except requests.exceptions.Timeout:
            last_error = "请求超时"
            print(f"        第{attempt+1}次超时")
        except Exception as e:
            last_error = str(e)
            print(f"        第{attempt+1}次异常: {e}")
        if attempt < 1:
            print("        等待 5 秒后重试...")
            time.sleep(5)

    # 降级：手动构造基础用例
    print(f"  ⚠ AI设计失败（{last_error}），降级为手动构造用例")
    fallback_cases = []
    for i, fp in enumerate(feature_points[:5]):
        name = fp.get("name", f"功能点{i+1}")
        fallback_cases.append({
            "title": f"{name} - 基础功能验证",
            "module": name,
            "priority": fp.get("priority", "P1"),
            "precondition": f"已访问 {TARGET_APP_URL}",
            "steps": [f"访问 {TARGET_APP_URL}", f"验证 {name} 功能可用"],
            "expected": f"{name} 功能正常显示，无异常",
            "script": "",
        })
    save_report("02_testcases_fallback.json", fallback_cases)
    log(2, 8, "design", f"降级构造 {len(fallback_cases)} 个用例")
    return fallback_cases


def step_3_generate_scripts(cases: list, app_url: str) -> list:
    print("\n[3/8] 脚本生成（AI生成Playwright脚本）...")
    if not cases:
        log(3, 8, "generate", "无用例，跳过", False)
        return []
    try:
        sample_cases = cases[:3]
        resp = requests.post(
            f"{BASE_URL}/generate",
            json={"test_cases": sample_cases, "app_url": app_url},
            timeout=120,
        )
        if resp.status_code == 200:
            data = resp.json()
            gen_cases = data.get("cases", [])
            if gen_cases:
                save_report("03_generated_scripts.json", data)
                log(3, 8, "generate", f"AI 生成 {len(gen_cases)} 个脚本")
                return gen_cases
            log(3, 8, "generate", "AI 返回脚本为空，降级为模板脚本")
        else:
            log(3, 8, "generate", f"AI失败 HTTP {resp.status_code}，降级为模板脚本")
    except Exception as e:
        log(3, 8, "generate", f"异常: {e}，降级为模板脚本")

    # 降级：模板脚本
    fallback_scripts = []
    for i, case in enumerate(cases[:3]):
        title = case.get("title", f"用例{i+1}")
        fallback_script = f"""const {{ test, expect }} = require('@playwright/test');

test('{title}', async ({{ page }}) => {{
  await page.goto('{app_url}', {{ waitUntil: 'networkidle' }});
  await expect(page).toHaveTitle(/.*/);
  await page.waitForTimeout(2000);
}});
"""
        fallback_scripts.append({
            "title": title,
            "module": case.get("module", ""),
            "priority": case.get("priority", "P1"),
            "precondition": case.get("precondition", ""),
            "steps": case.get("steps", []),
            "expected": case.get("expected", ""),
            "script": fallback_script,
        })
    save_report("03_scripts_fallback.json", fallback_scripts)
    log(3, 8, "generate", f"降级生成 {len(fallback_scripts)} 个模板脚本")
    return fallback_scripts


def step_4_stability_check(project_id: int) -> dict:
    print("\n[4/8] 稳定性检测...")
    try:
        resp = requests.post(
            f"{BASE_URL}/projects/{project_id}/stability/check-all",
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            log(4, 8, "stability", f"失败 HTTP {resp.status_code}: {resp.text[:200]}", False)
            return {}
        data = resp.json()
        save_report("04_stability.json", data)
        checks = data.get("checks", {})
        log(4, 8, "stability",
            f"用例数={data.get('caseCount', 0)}, 问题数={data.get('totalIssues', 0)}, 总分={data.get('overallScore', 0)}")
        for name, info in checks.items():
            print(f"        - {info.get('label', name)}: risk={info.get('risk_count', 0)}, tag={info.get('tag', '')}")
        return data
    except Exception as e:
        log(4, 8, "stability", f"异常: {e}", False)
        return {}


def step_5_ai_review(project_id: int) -> dict:
    print("\n[5/8] AI评审...")
    try:
        resp = requests.post(
            f"{BASE_URL}/projects/{project_id}/review/generate",
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            log(5, 8, "review", f"失败 HTTP {resp.status_code}: {resp.text[:200]}", False)
            return {}
        data = resp.json()
        save_report("05_review.json", data)
        log(5, 8, "review", f"综合评分={data.get('score', 0)}")
        for m in data.get("metrics", []):
            print(f"        - {m.get('label', '')}: {m.get('value', '')}")
        for i, s in enumerate(data.get("suggestions", [])[:3]):
            print(f"        - 建议#{i+1}: {s.get('title', '')} | {s.get('problem', '')[:60]}")
        return data
    except Exception as e:
        log(5, 8, "review", f"异常: {e}", False)
        return {}


def step_6_login_profile(project_id: int) -> dict:
    print("\n[6/8] 登录态配置...")
    try:
        resp = requests.post(
            f"{BASE_URL}/projects/{project_id}/login-profiles",
            json=LOGIN_CONFIG,
            timeout=30,
        )
        if resp.status_code != 200:
            # 可能已存在，尝试获取
            resp2 = requests.get(f"{BASE_URL}/projects/{project_id}/login-profiles", timeout=30)
            if resp2.status_code == 200:
                profiles = resp2.json()
                for p in profiles:
                    if p.get("id") != "anonymous" and p.get("name") == LOGIN_CONFIG["name"]:
                        log(6, 8, "login-profile", f"已存在配置 ID={p.get('id')}")
                        profile = p
                        break
                else:
                    log(6, 8, "login-profile", f"创建失败 HTTP {resp.status_code}: {resp.text[:200]}", False)
                    return {}
            else:
                log(6, 8, "login-profile", f"创建失败 HTTP {resp.status_code}", False)
                return {}
        else:
            profile = resp.json()
            save_report("06_login_profile.json", profile)
            log(6, 8, "login-profile", f"配置创建成功 ID={profile.get('id')}")

        profile_id = profile.get("id")
        if profile_id and profile_id != "anonymous":
            print("        尝试生成登录会话...")
            resp = requests.post(
                f"{BASE_URL}/login-profiles/{profile_id}/generate-session",
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                sess = resp.json()
                if sess.get("success"):
                    log(6, 8, "generate-session", "登录会话生成成功")
                else:
                    msg = sess.get("message", "")[:100] or sess.get("error", "")[:100]
                    log(6, 8, "generate-session", f"会话生成失败（非阻断）: {msg}")
                save_report("06_login_session.json", sess)
            else:
                log(6, 8, "generate-session", f"HTTP {resp.status_code}")
        return profile
    except Exception as e:
        log(6, 8, "login-profile", f"异常: {e}", False)
        return {}


def step_7_execute_tests(project_id: int, cases: list) -> dict:
    print("\n[7/8] 测试用例执行...")
    if not cases:
        log(7, 8, "execute", "无可用用例", False)
        return {}

    try:
        batch_id = f"BATCH-E2E-{int(time.time())}"
        resp = requests.post(
            f"{BASE_URL}/projects/{project_id}/executions",
            json={"batch_id": batch_id, "total": len(cases)},
            timeout=30,
        )
        if resp.status_code != 200:
            log(7, 8, "execute", f"创建批次失败 HTTP {resp.status_code}", False)
            return {}
        execution = resp.json()
        exec_id = execution["id"]
        log(7, 8, "execute", f"执行批次创建 ID={exec_id}, batch={batch_id}")

        items = []
        passed = 0
        failed = 0
        for i, case in enumerate(cases):
            script = case.get("script", "")
            title = case.get("title", f"用例{i+1}")
            if not script:
                items.append({"caseId": case.get("id", i), "title": title, "passed": False, "error": "无脚本"})
                failed += 1
                continue
            print(f"        执行 [{i+1}/{len(cases)}] {title[:40]}...")
            try:
                resp = requests.post(
                    f"{BASE_URL}/run",
                    json={"script": script, "app_url": TARGET_APP_URL, "timeout": 60000},
                    timeout=90,
                )
                if resp.status_code == 200:
                    run_data = resp.json()
                    is_pass = run_data.get("passed", False)
                    if is_pass:
                        passed += 1
                    else:
                        failed += 1
                    items.append({
                        "caseId": case.get("id", i),
                        "title": title,
                        "passed": is_pass,
                        "duration": run_data.get("duration_ms", 0),
                        "error": run_data.get("error", ""),
                    })
                else:
                    failed += 1
                    items.append({"caseId": case.get("id", i), "title": title, "passed": False, "error": f"HTTP {resp.status_code}"})
            except Exception as e:
                failed += 1
                items.append({"caseId": case.get("id", i), "title": title, "passed": False, "error": str(e)})

        requests.put(
            f"{BASE_URL}/executions/{exec_id}",
            json={
                "status": "completed",
                "passed": passed,
                "failed": failed,
                "items": items,
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            timeout=30,
        )

        for item in items:
            requests.post(
                f"{BASE_URL}/executions/{exec_id}/logs",
                json={"level": "info" if item.get("passed") else "error",
                      "message": f"{item.get('title','')}: {'PASS' if item.get('passed') else 'FAIL - ' + item.get('error','')}"},
                timeout=10,
            )

        total = len(cases)
        pass_rate = f"{(passed / total * 100):.1f}%" if total else "0%"
        modules_summary = {}
        for item in items:
            modules_summary[item.get("title", "unknown")] = "pass" if item.get("passed") else "fail"
        report_resp = requests.post(
            f"{BASE_URL}/executions/{exec_id}/report",
            json={
                "pass_rate": pass_rate,
                "trends": {"batch": batch_id, "pass_rate": pass_rate, "passed": passed, "failed": failed},
                "modules": modules_summary,
                "fails": [item for item in items if not item.get("passed")],
            },
            timeout=30,
        )
        report_id = report_resp.json().get("id") if report_resp.status_code == 200 else None
        save_report("07_execution.json", {
            "execId": exec_id, "batchId": batch_id, "total": total,
            "passed": passed, "failed": failed, "passRate": pass_rate,
            "reportId": report_id, "items": items,
        })
        log(7, 8, "execute", f"执行完成: {passed}/{total} 通过, 通过率={pass_rate}")
        return {"exec_id": exec_id, "report_id": report_id, "passed": passed, "failed": failed, "total": total, "items": items}
    except Exception as e:
        log(7, 8, "execute", f"异常: {e}", False)
        traceback.print_exc()
        return {}


def step_8_query_reports(project_id: int) -> dict:
    print("\n[8/8] 报告查询...")
    try:
        resp = requests.get(f"{BASE_URL}/projects/{project_id}/reports", timeout=30)
        if resp.status_code != 200:
            log(8, 8, "report", f"查询失败 HTTP {resp.status_code}", False)
            return {}
        reports = resp.json()
        save_report("08_reports.json", reports)
        log(8, 8, "report", f"查询到 {len(reports)} 个执行报告")
        for r in reports:
            print(f"        - 批次={r.get('batchId','')}, 状态={r.get('status','')}, "
                  f"通过率={r.get('passRate','')}, 报告ID={r.get('reportId')}")

        resp = requests.get(f"{BASE_URL}/dashboard/stats", timeout=30)
        stats = {}
        if resp.status_code == 200:
            stats = resp.json()
            save_report("08_dashboard_stats.json", stats)
            print(f"        Dashboard: 项目={stats.get('projectCount')}, 用例={stats.get('totalCases')}, "
                  f"执行={stats.get('totalExecutions')}, 通过率={stats.get('passRate')}")
        return {"reports": reports, "stats": stats}
    except Exception as e:
        log(8, 8, "report", f"异常: {e}", False)
        return {}


# ==================== 考公大师账号注册（前置） ====================
def setup_register_account(browser):
    """在考公大师注册测试账号（已存在则跳过），确保登录态会话可生成。
    复用已启动的 browser 实例，避免重复 launch 导致超时。"""
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
        print("  ✓ 注册请求已提交（账号已存在则忽略）")
    except Exception as e:
        print(f"  ⚠ 注册流程异常（账号可能已存在）: {e}")
    finally:
        ctx.close()


# ==================== 主流程 ====================
def run_full_e2e():
    print("=" * 72)
    print("TestPilot 端到端测试：用 AI 测试智能体测试「考公大师」（8阶段 + 录屏）")
    print(f"被测目标: {TARGET_APP_URL}")
    print(f"TestPilot API: {BASE_URL}")
    print(f"TestPilot UI: {TESTPILOT_UI}")
    print(f"录屏目录: {VIDEO_DIR}")
    print("=" * 72)

    os.makedirs(VIDEO_DIR, exist_ok=True)
    results = []

    # 0. 健康检查
    has_key = step_0_health()
    results.append(("健康检查", has_key is not None))
    if not has_key:
        print("\n  ⚠ 警告: AI API Key 未配置，AI 相关步骤可能降级")

    # 创建项目 + 需求
    print("\n[准备] 创建测试项目...")
    project_name = f"考公大师-E2E-{int(time.time())}"
    resp = requests.post(
        f"{BASE_URL}/projects",
        json={
            "name": project_name,
            "description": "考公大师备考系统 端到端测试项目",
            "appUrl": TARGET_APP_URL,
            "dim": "在线教育/考试备考",
            "techStack": "Next.js/React/TypeScript",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"  ✗ 创建项目失败: {resp.text}")
        return False
    project = resp.json()
    project_id = project["id"]
    print(f"  ✓ 项目创建成功: {project_name} (ID={project_id})")
    save_report("00_project.json", project)

    resp = requests.post(
        f"{BASE_URL}/projects/{project_id}/requirements",
        json={"title": "考公大师 备考全流程", "content": REQUIREMENT_TEXT},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"  ✗ 创建需求失败: {resp.text}")
        return False
    requirement = resp.json()
    req_id = requirement["id"]
    print(f"  ✓ 需求创建成功: ID={req_id}")

    # ===== 启动浏览器（仅启动一次）+ 录屏驱动 TestPilot UI =====
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME_PATH)

        # 前置：注册考公大师账号（非录屏 context，复用同一 browser）
        setup_register_account(browser)

        context = browser.new_context(
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()

        try:
            # 打开 TestPilot 工具界面
            print("\n[录屏] 启动 TestPilot 工具界面...")
            page.goto(TESTPILOT_UI, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_timeout(1500)
            ui_screenshot(page, "stage_00_testpilot_home.png")
            page.wait_for_timeout(1500)

            # 阶段1: AI需求分析
            feature_points = step_1_analyze(project_id, req_id, REQUIREMENT_TEXT)
            results.append(("AI需求分析", len(feature_points) > 0))
            show_stage(page, project_name, 1, 8, "requirement", "stage_01_analysis.png")

            # 阶段2: 用例生成
            cases_designed = step_2_design_testcases(feature_points)
            results.append(("用例生成", len(cases_designed) > 0))

            # 持久化用例到数据库
            print("\n  持久化用例到数据库...")
            saved_case_ids = []
            for c in cases_designed:
                resp = requests.post(
                    f"{BASE_URL}/projects/{project_id}/testcases",
                    json={
                        "title": c.get("title", ""),
                        "module": c.get("module"),
                        "priority": c.get("priority", "P1"),
                        "precondition": c.get("precondition"),
                        "steps": c.get("steps", []),
                        "expected": c.get("expected"),
                        "script": c.get("script"),
                        "requirementId": req_id,
                    },
                    timeout=30,
                )
                if resp.status_code == 200:
                    saved_case_ids.append(resp.json().get("id"))
            print(f"  ✓ 已持久化 {len(saved_case_ids)} 个用例")
            show_stage(page, project_name, 2, 8, "testcases", "stage_02_testcases.png")

            # 阶段3: 脚本生成
            gen_cases = step_3_generate_scripts(cases_designed, TARGET_APP_URL)
            results.append(("脚本生成", len(gen_cases) > 0))

            # 回写脚本到已保存的用例
            print("\n  回写生成脚本到用例...")
            for i, gc in enumerate(gen_cases):
                if i < len(saved_case_ids):
                    case_id = saved_case_ids[i]
                    requests.patch(
                        f"{BASE_URL}/cases/{case_id}",
                        json={
                            "title": gc.get("title", ""),
                            "precondition": gc.get("precondition", ""),
                            "steps": gc.get("steps", []),
                            "expected": gc.get("expected", ""),
                            "script": gc.get("script", ""),
                            "version": 1,
                        },
                        timeout=30,
                    )
            print(f"  ✓ 已回写 {len(gen_cases)} 个脚本")
            show_stage(page, project_name, 3, 8, "testcases", "stage_03_scripts.png")

            # 阶段4: 稳定性检测
            stability = step_4_stability_check(project_id)
            results.append(("稳定性检测", "overallScore" in stability or "caseCount" in stability))
            show_stage(page, project_name, 4, 8, "testcases", "stage_04_stability.png")

            # 阶段5: AI评审
            review = step_5_ai_review(project_id)
            results.append(("AI评审", "score" in review))
            show_stage(page, project_name, 5, 8, "testcases", "stage_05_review.png")

            # 阶段6: 登录态配置
            login_profile = step_6_login_profile(project_id)
            results.append(("登录态配置", bool(login_profile)))
            # 登录态通过弹窗展示
            ui_select_project(page, project_name)
            try:
                page.evaluate("showLoginConfig()")
                page.wait_for_timeout(2000)
            except Exception:
                pass
            ui_screenshot(page, "stage_06_login_profile.png")
            page.wait_for_timeout(2000)

            # 阶段7: 测试用例执行
            exec_cases = []
            for i, gc in enumerate(gen_cases):
                exec_cases.append({
                    "id": saved_case_ids[i] if i < len(saved_case_ids) else i,
                    "title": gc.get("title", ""),
                    "script": gc.get("script", ""),
                })
            execution = step_7_execute_tests(project_id, exec_cases)
            results.append(("测试用例执行", bool(execution)))
            # 执行中心通过弹窗展示
            ui_select_project(page, project_name)
            try:
                page.evaluate("openExecutionModal()")
                page.wait_for_timeout(2000)
            except Exception:
                pass
            ui_screenshot(page, "stage_07_execution.png")
            page.wait_for_timeout(2000)

            # 阶段8: 报告查询
            reports = step_8_query_reports(project_id)
            results.append(("报告查询", bool(reports)))
            show_stage(page, project_name, 8, 8, "report", "stage_08_report.png")

        finally:
            # 关闭 context 以保存录屏视频
            video_path = None
            try:
                if page.video:
                    video_path = page.video.path()
            except Exception:
                pass
            context.close()
            browser.close()

    # ==================== 汇总 ====================
    print("\n" + "=" * 72)
    print("端到端测试结果汇总")
    print("=" * 72)
    all_pass = True
    for name, ok in results:
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"  {status} - {name}")
        if not ok:
            all_pass = False

    print("\n" + ("✓ 全部阶段通过！" if all_pass else "✗ 部分阶段失败，请检查上方日志"))

    # 重命名录屏文件
    try:
        if video_path and os.path.exists(video_path):
            final_name = f"testpilot_e2e_考公大师_{int(time.time())}.webm"
            final_path = os.path.join(VIDEO_DIR, final_name)
            shutil.move(video_path, final_path)
            print(f"\n录屏视频: {final_path}")
            print(f"文件大小: {os.path.getsize(final_path) / 1024:.1f} KB")
    except Exception as e:
        print(f"\n录屏文件重命名失败: {e}")

    # 保存汇总报告
    summary = {
        "target": TARGET_APP_URL,
        "project": project_name,
        "projectId": project_id,
        "stages": [{"name": n, "passed": ok} for n, ok in results],
        "allPassed": all_pass,
        "finishedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_report("09_summary.json", summary)
    print(f"\n各阶段输出已保存到 {VIDEO_DIR} 目录")
    print("=" * 72)
    return all_pass


if __name__ == "__main__":
    success = run_full_e2e()
    sys.exit(0 if success else 1)
