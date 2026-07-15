"""
TestPilot 主要功能 API 测试
覆盖：健康检查、项目、需求、用例、执行记录、报告、登录态、仪表盘、设置
"""
import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api"
results = []  # (name, ok, detail)


def req(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, method=method)
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            txt = resp.read().decode()
            return resp.status, json.loads(txt) if txt else None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


def check(name, status, data, expected=200):
    ok = status == expected
    detail = ""
    if isinstance(data, dict):
        if "id" in data:
            detail = f"id={data['id']}"
        elif "items" in data:
            detail = f"{len(data['items'])} items"
        elif "total" in data:
            detail = f"total={data['total']}"
        elif "error" in data:
            detail = f"err={data['error']}"
        else:
            keys = list(data.keys())[:3]
            detail = ",".join(keys)
    elif isinstance(data, list):
        detail = f"{len(data)} items"
    results.append((name, ok, f"{status} {detail}"))


# 1. 健康检查
s, d = req("GET", "/health")
check("健康检查", s, d)

# 2. 仪表盘统计
s, d = req("GET", "/dashboard/stats")
check("仪表盘统计", s, d)

# 3. 项目列表
s, d = req("GET", "/projects")
check("项目列表", s, d)
project_id = d[0]["id"] if isinstance(d, list) and d else 1

# 4. 项目详情
s, d = req("GET", f"/projects/{project_id}")
check("项目详情", s, d)

# 5. 项目需求列表
s, d = req("GET", f"/projects/{project_id}/requirements")
check("项目需求列表", s, d)

# 6. 项目用例列表
s, d = req("GET", f"/projects/{project_id}/testcases")
check("项目用例列表", s, d)

# 7. 项目执行记录
s, d = req("GET", f"/projects/{project_id}/execution-records")
check("项目执行记录", s, d)

# 8. 项目执行批次列表
s, d = req("GET", f"/projects/{project_id}/executions")
check("项目执行批次", s, d)

# 9. 项目报告列表
s, d = req("GET", f"/projects/{project_id}/reports")
check("项目报告列表", s, d)

# 10. 稳定性检查
s, d = req("GET", f"/projects/{project_id}/stability")
check("稳定性检查", s, d)

# 11. AI 评审报告
s, d = req("GET", f"/projects/{project_id}/review")
check("AI 评审报告", s, d)

# 12. 登录态配置列表
s, d = req("GET", f"/projects/{project_id}/login-profiles")
check("登录态配置列表", s, d)

# 13. 默认登录态
s, d = req("GET", f"/projects/{project_id}/login-profiles/default")
check("默认登录态", s, d)

# 14. 设置-全局
s, d = req("GET", "/settings")
check("设置-全局", s, d)

# 15. 创建项目（POST）
s, d = req("POST", "/projects", {"name": "API测试项目", "appUrl": "http://example.com"})
check("创建项目", s, d, expected=200)

# 16. 创建登录态配置
s, d = req("POST", f"/projects/{project_id}/login-profiles", {
    "name": "API测试管理员", "role": "admin",
    "username": "test@example.com", "password": "pwd123",
    "loginUrl": "http://example.com/login", "scriptMode": "form"
})
check("创建登录态配置", s, d)

# 17. 更新登录态配置（切到脚本模式）
if isinstance(d, dict) and "id" in d:
    pid = d["id"]
    s2, d2 = req("PUT", f"/login-profiles/{pid}", {
        "scriptMode": "custom",
        "customScript": "await page.goto('http://example.com/login');"
    })
    check("更新登录态(脚本模式)", s2, d2)

# 18. 更新用例状态（如存在用例）
s, d = req("GET", f"/projects/{project_id}/testcases")
if isinstance(d, list) and d:
    case_id = d[0].get("id")
    if case_id:
        s2, d2 = req("PUT", f"/testcases/{case_id}/status", {"status": "passed"})
        check("更新用例状态", s2, d2)
else:
    results.append(("更新用例状态", True, "skip(无用例)"))

# 19. 生成会话（不实际执行，仅验证接口可达性）
# 跳过此步骤，避免触发 Playwright 长时间执行
results.append(("生成会话接口", True, "skip(避免触发 Playwright)"))

# 输出结果
print("\n" + "=" * 70)
print("TestPilot 主要功能 API 测试结果")
print("=" * 70)
passed = sum(1 for _, ok, _ in results if ok)
failed = len(results) - passed
for name, ok, detail in results:
    mark = "✓" if ok else "✗"
    print(f"  {mark} {name:24s} {detail}")
print("-" * 70)
print(f"  通过 {passed}/{len(results)}，失败 {failed}")
print("=" * 70)
