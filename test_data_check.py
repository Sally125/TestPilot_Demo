# -*- coding: utf-8 -*-
"""快速验证各项目的关联数据是否完整"""
import urllib.request, json

BASE = "http://localhost:8000/api"

def get(path):
    try:
        r = urllib.request.urlopen(f"{BASE}{path}", timeout=5)
        return json.loads(r.read())
    except Exception as e:
        return f"ERROR: {e}"

projects = get("/projects")
print(f"项目总数: {len(projects)}")
print("=" * 70)
for p in projects:
    pid = p["id"]
    reqs = get(f"/projects/{pid}/requirements")
    cases = get(f"/projects/{pid}/testcases")
    execs = get(f"/projects/{pid}/executions")
    reports = get(f"/projects/{pid}/reports")
    n_cases = len(cases.get("items", [])) if isinstance(cases, dict) else 0
    n_reqs = len(reqs) if isinstance(reqs, list) else 0
    n_execs = len(execs) if isinstance(execs, list) else 0
    n_reports = len(reports) if isinstance(reports, list) else 0
    print(f"项目{pid} [{p['name'][:20]}]: 需求={n_reqs} 用例={n_cases} 执行={n_execs} 报告={n_reports}")
print("=" * 70)
print("数据验证完成")
