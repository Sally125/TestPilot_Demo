"""端到端测试：从需求分析到用例执行完整流程

测试流程：
1. 健康检查
2. 创建项目
3. 创建需求
4. AI需求分析（流式）
5. 生成测试用例
6. 稳定性检查
7. AI评审
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000/api"
TIMEOUT = 120

def log(step, msg, ok=True):
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} [{step}] {msg}")

def test_full_flow():
    print("\n" + "="*60)
    print("端到端测试：从需求分析到用例执行")
    print("="*60)

    # 0. 健康检查
    print("\n[0/7] 健康检查...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        if resp.status_code == 200:
            log("health", "后端服务正常", True)
        else:
            log("health", f"健康检查返回 {resp.status_code}", False)
            return
    except Exception as e:
        log("health", f"无法连接后端: {e}", False)
        return

    project_name = f"E2E_Test_{int(time.time())}"

    # 1. 创建项目
    print("\n[1/7] 创建项目...")
    resp = requests.post(f"{BASE_URL}/projects",
                        json={"name": project_name, "description": "端到端测试项目"},
                        timeout=30)
    if resp.status_code != 200:
        log("create_project", f"创建失败: {resp.text}", False)
        return
    project = resp.json()
    project_id = project["id"]
    log("create_project", f"项目创建成功: {project_name} (ID={project_id})")

    # 2. 创建需求
    print("\n[2/7] 创建需求...")
    requirement_text = "用户登录功能：支持邮箱和手机号登录，密码长度至少6位，支持忘记密码功能"
    resp = requests.post(f"{BASE_URL}/projects/{project_id}/requirements",
                        json={"title": "登录功能测试", "content": requirement_text},
                        timeout=30)
    if resp.status_code != 200:
        log("create_requirement", f"创建失败: {resp.text}", False)
        return
    requirement = resp.json()
    req_id = requirement["id"]
    log("create_requirement", f"需求创建成功: ID={req_id}")

    # 3. AI需求分析（流式）
    print("\n[3/7] AI需求分析...")
    try:
        resp = requests.post(f"{BASE_URL}/analyze/stream",
                            json={"project_id": project_id, "requirement_id": req_id,
                                  "requirement_text": requirement_text, "app_url": ""},
                            stream=True, timeout=TIMEOUT)
        if resp.status_code != 200:
            log("analyze", f"分析请求失败: HTTP {resp.status_code}", False)
            return

        analysis_result = None
        char_count = 0
        for line in resp.iter_lines():
            if line:
                try:
                    data_str = line.decode('utf-8').strip()
                    if data_str.startswith("data:"):
                        data = json.loads(data_str[5:].strip())
                        if data.get("type") == "progress":
                            char_count += len(data.get("content", ""))
                        elif data.get("type") == "complete":
                            analysis_result = data
                            break
                        elif data.get("type") == "error":
                            log("analyze", f"分析错误: {data.get('message', '')}", False)
                            return
                except Exception as e:
                    print(f"    (解析警告: {e})")
                    continue

        if not analysis_result:
            log("analyze", "未收到分析结果", False)
            return

        feature_points = analysis_result.get("feature_points", [])
        log("analyze", f"需求分析完成，提取 {len(feature_points)} 个功能点，接收 {char_count} 字符")

        # 保存分析结果到需求
        resp = requests.put(f"{BASE_URL}/requirements/{req_id}/analysis",
                     json={"analysis_result": analysis_result}, timeout=30)
        if resp.status_code == 200:
            log("save_analysis", "分析结果已保存到需求")
        else:
            log("save_analysis", f"保存分析结果失败: {resp.status_code} {resp.text}", False)

    except Exception as e:
        log("analyze", f"分析失败: {e}", False)
        return

    # 4. 生成测试用例
    print("\n[4/7] 生成测试用例...")
    try:
        resp = requests.post(f"{BASE_URL}/generate",
                            json={"feature_points": feature_points, "app_url": ""},
                            timeout=TIMEOUT)
        if resp.status_code != 200:
            log("generate", f"生成失败: HTTP {resp.status_code}: {resp.text}", False)
            return
        gen_result = resp.json()
        cases = gen_result.get("cases", [])
        log("generate", f"生成 {len(cases)} 个测试用例")

        # 持久化测试用例
        for c in cases:
            resp = requests.post(f"{BASE_URL}/projects/{project_id}/testcases",
                                json={
                                    "title": c.get("title", ""),
                                    "module": c.get("module"),
                                    "priority": c.get("priority", "P1"),
                                    "precondition": c.get("precondition"),
                                    "steps": c.get("steps", []),
                                    "expected": c.get("expected"),
                                    "script": c.get("script"),
                                    "requirementId": req_id
                                }, timeout=30)
            if resp.status_code != 200:
                log("save_case", f"保存用例失败: {resp.text}", False)
        log("save_cases", f"已持久化 {len(cases)} 个测试用例到数据库")

    except Exception as e:
        log("generate", f"生成用例失败: {e}", False)
        return

    # 5. 稳定性检查
    print("\n[5/7] 稳定性检查...")
    try:
        resp = requests.post(f"{BASE_URL}/projects/{project_id}/stability/check-all",
                            timeout=TIMEOUT)
        if resp.status_code != 200:
            log("stability", f"稳定性检查失败: HTTP {resp.status_code}: {resp.text}", False)
            return
        stability = resp.json()
        checks = stability.get("checks", {})
        log("stability", f"稳定性检查完成，总用例数={stability.get('caseCount', 0)}，问题数={stability.get('totalIssues', 0)}")
        for check_name, check_data in checks.items():
            log("stability", f"  - {check_data.get('label', check_name)}: risk={check_data.get('risk_count', 0)}, tag={check_data.get('tag', '')}")

    except Exception as e:
        log("stability", f"稳定性检查失败: {e}", False)
        return

    # 6. AI评审
    print("\n[6/7] AI评审...")
    try:
        resp = requests.post(f"{BASE_URL}/projects/{project_id}/review/generate",
                            timeout=TIMEOUT)
        if resp.status_code != 200:
            log("review", f"AI评审失败: HTTP {resp.status_code}: {resp.text}", False)
            return
        review = resp.json()
        log("review", f"AI评审完成，综合评分={review.get('score', 0)}")
        for m in review.get("metrics", []):
            log("review", f"  - {m.get('label', '')}: {m.get('value', '')}")
        for i, s in enumerate(review.get("suggestions", [])):
            log("review", f"  - 建议#{i+1}: {s.get('title', '')}")

    except Exception as e:
        log("review", f"AI评审失败: {e}", False)
        return

    # 7. 验证数据持久化
    print("\n[7/7] 验证数据持久化...")
    try:
        # 验证测试用例
        resp = requests.get(f"{BASE_URL}/projects/{project_id}/testcases", timeout=30)
        if resp.status_code == 200:
            tc_data = resp.json()
            log("verify", f"数据库用例数: {tc_data.get('total', 0)}")

        # 验证稳定性报告
        resp = requests.get(f"{BASE_URL}/projects/{project_id}/stability", timeout=30)
        if resp.status_code == 200:
            stab_data = resp.json()
            log("verify", f"稳定性报告存在: {bool(stab_data)}")

        # 验证评审报告
        resp = requests.get(f"{BASE_URL}/projects/{project_id}/review", timeout=30)
        if resp.status_code == 200:
            rev_data = resp.json()
            log("verify", f"评审报告存在: {bool(rev_data)}")

    except Exception as e:
        log("verify", f"验证失败: {e}", False)

    print("\n" + "="*60)
    print("[PASS] 端到端测试全部通过！")
    print("="*60)

if __name__ == "__main__":
    test_full_flow()
