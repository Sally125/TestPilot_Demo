# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 生成登录会话快照
- Location: testpilot-backend\generated\.runtime\bbda1c86\test.spec.ts:3:5

# Error details

```
Test timeout of 60000ms exceeded.
```

```
Error: locator.fill: Test timeout of 60000ms exceeded.
Call log:
  - waiting for getByPlaceholder(/用户名|邮箱|email|username/i)

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e2]:
    - text: This is just a demo of TodoMVC for testing, not the
    - link "real TodoMVC app." [ref=e3] [cursor=pointer]:
      - /url: https://todomvc.com/
  - generic [ref=e6]:
    - heading "todos" [level=1] [ref=e7]
    - textbox "What needs to be done?" [active] [ref=e8]
  - contentinfo [ref=e9]:
    - paragraph [ref=e10]: Double-click to edit a todo
    - paragraph [ref=e11]:
      - text: Created by
      - link "Remo H. Jansen" [ref=e12] [cursor=pointer]:
        - /url: http://github.com/remojansen/
    - paragraph [ref=e13]:
      - text: Part of
      - link "TodoMVC" [ref=e14] [cursor=pointer]:
        - /url: http://todomvc.com
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('生成登录会话快照', async ({ page }) => {
  4  |   // 1. 访问登录页
  5  |   await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  | 
  7  |   // 2. 填入凭证
> 8  |   await (page.getByPlaceholder(/用户名|邮箱|email|username/i)).fill('admin@test.com');
     |                                                           ^ Error: locator.fill: Test timeout of 60000ms exceeded.
  9  |   await (page.getByPlaceholder(/密码|password/i)).fill('pwd123');
  10 | 
  11 |   // 3. 点击提交
  12 |   await (page.getByRole('button', { name: /登录|sign in|log in/i })).click();
  13 | 
  14 |   // 4. 等待登录成功
  15 |   await page.waitForLoadState('networkidle', { timeout: 10000 });
  16 | 
  17 |   // 5. 保存会话快照
  18 |   await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/1/profile-2.json' });
  19 | });
  20 | 
```