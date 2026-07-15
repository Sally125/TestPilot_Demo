"""验证 '未提供' 占位符替换是否生效"""
import json
import urllib.request

script = '''import { test, expect } from "@playwright/test";

test("goto test", async ({ page }) => {
  await page.goto("未提供", { waitUntil: "domcontentloaded" });
  await expect(page.locator("body")).toBeVisible();
});
'''

body = json.dumps({
    "script": script,
    "app_url": "http://localhost:3001/login",
    "timeout": 30000
}).encode()

req = urllib.request.Request(
    "http://localhost:8000/api/run",
    data=body,
    method="POST",
    headers={"Content-Type": "application/json"}
)

try:
    r = urllib.request.urlopen(req, timeout=60)
    d = json.loads(r.read())
    print("passed:", d.get("passed"))
    print("error:", (d.get("error") or "")[:200])
    print("duration_ms:", d.get("duration_ms"))
except urllib.error.HTTPError as e:
    print("HTTP error:", e.code, e.read().decode()[:300])
except Exception as e:
    print("Exception:", e)
