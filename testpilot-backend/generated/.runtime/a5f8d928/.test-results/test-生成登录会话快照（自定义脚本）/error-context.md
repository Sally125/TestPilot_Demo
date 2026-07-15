# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 生成登录会话快照（自定义脚本）
- Location: testpilot-backend\generated\.runtime\a5f8d928\test.spec.ts:3:5

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:28089/login
Call log:
  - navigating to "http://localhost:28089/login", waiting until "networkidle"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('生成登录会话快照（自定义脚本）', async ({ page }) => {
  4  |   // ===== 用户自定义登录代码 开始 =====
  5  |   // newbee-mall 登录脚本（绕过验证码）
  6  | const { chromium } = require('playwright');
  7  | (async () => {
  8  |   const browser = await chromium.launch();
  9  |   const context = await browser.newContext();
  10 |   const page = await context.newPage();
> 11 |   await page.goto('http://localhost:28089/login', { waitUntil: 'networkidle' });
     |              ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:28089/login
  12 |   await page.fill("input[name='loginName']", '13700002703');
  13 |   await page.fill("input[name='password']", '123456');
  14 |   // 直接提交（后端 session 中无验证码时部分情况可绕过）
  15 |   await page.click("input[type='submit']");
  16 |   await page.waitForTimeout(3000);
  17 |   await context.storageState({ path: process.env.STORAGE_STATE_PATH });
  18 |   await browser.close();
  19 | })();
  20 |   // ===== 用户自定义登录代码 结束 =====
  21 | 
  22 |   // 自动追加：保存会话快照
  23 |   await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/15/profile-10.json' });
  24 | });
  25 | 
```