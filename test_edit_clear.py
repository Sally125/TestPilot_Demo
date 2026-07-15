# -*- coding: utf-8 -*-
"""验证清空字段（空字符串）的边缘情况"""
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


print("测试清空 description 字段（传空字符串）")
print("-" * 50)
orig = http("GET", f"/projects/{PROJECT_ID}")[1]
print(f"清空前 description: {orig.get('description')}")

http("PUT", f"/projects/{PROJECT_ID}", {"description": ""})
after = http("GET", f"/projects/{PROJECT_ID}")[1]
print(f"清空后 description: {repr(after.get('description'))}")

ok_clear = after.get("description") == ""
print(f"清空测试: {'PASS' if ok_clear else 'FAIL'}")

print()
print("恢复原始数据")
http("PUT", f"/projects/{PROJECT_ID}", {"description": orig.get("description")})
restored = http("GET", f"/projects/{PROJECT_ID}")[1]
print(f"恢复后 description: {restored.get('description')}")
