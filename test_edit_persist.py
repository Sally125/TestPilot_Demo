# -*- coding: utf-8 -*-
"""验证项目编辑保存持久化修复"""
import json
import urllib.request

BASE = "http://localhost:8000/api"
PROJECT_ID = 1


def http(method, path, body=None):
    url = f"{BASE}{path}"
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def get_project(pid):
    _, data = http("GET", f"/projects/{pid}")
    return data


print("=" * 60)
print("1. 获取项目原始数据")
print("=" * 60)
orig = get_project(PROJECT_ID)
print(f"  name: {orig.get('name')}")
print(f"  description: {orig.get('description')}")
print(f"  appUrl: {orig.get('appUrl')}")

print()
print("=" * 60)
print("2. PUT 更新项目（JSON body）")
print("=" * 60)
new_data = {
    "name": "TodoMVC测试项目_已更新",
    "description": "测试TodoMVC应用_已更新",
    "appUrl": "https://demo.playwright.dev/todomvc/updated/",
}
status, resp = http("PUT", f"/projects/{PROJECT_ID}", new_data)
print(f"  HTTP 状态: {status}")
print(f"  返回 name: {resp.get('name')}")
print(f"  返回 description: {resp.get('description')}")
print(f"  返回 appUrl: {resp.get('appUrl')}")
print(f"  返回 updatedAt: {resp.get('updatedAt')}")

print()
print("=" * 60)
print("3. 再次 GET 项目，验证持久化")
print("=" * 60)
after = get_project(PROJECT_ID)
print(f"  name: {after.get('name')}")
print(f"  description: {after.get('description')}")
print(f"  appUrl: {after.get('appUrl')}")

ok = (
    after.get("name") == new_data["name"]
    and after.get("description") == new_data["description"]
    and after.get("appUrl") == new_data["appUrl"]
)
print()
print("=" * 60)
print(f"结果: {'PASS - 持久化修复成功' if ok else 'FAIL - 仍失效'}")
print("=" * 60)

print()
print("=" * 60)
print("4. 恢复原始数据")
print("=" * 60)
restore = {
    "name": orig.get("name"),
    "description": orig.get("description"),
    "appUrl": orig.get("appUrl"),
}
status, resp = http("PUT", f"/projects/{PROJECT_ID}", restore)
restored = get_project(PROJECT_ID)
print(f"  已恢复 name: {restored.get('name')}")
print(f"  已恢复 appUrl: {restored.get('appUrl')}")
