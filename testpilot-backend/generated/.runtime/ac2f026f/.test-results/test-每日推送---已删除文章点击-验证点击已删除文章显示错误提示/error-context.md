# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 每日推送 - 已删除文章点击 >> 验证点击已删除文章显示错误提示
- Location: testpilot-backend\generated\.runtime\ac2f026f\test.spec.ts:20:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: locator.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByLabel('用户名')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e4]:
    - generic [ref=e5]:
      - heading "欢迎回来" [level=1] [ref=e6]
      - paragraph [ref=e7]: 登录考公大师，继续你的备考之旅
    - generic [ref=e8]:
      - generic [ref=e9]:
        - generic [ref=e10]: 邮箱
        - textbox "邮箱" [ref=e11]:
          - /placeholder: your@email.com
      - generic [ref=e12]:
        - generic [ref=e13]: 密码
        - textbox "密码" [ref=e14]:
          - /placeholder: ••••••••
      - button "登录" [ref=e15] [cursor=pointer]
    - paragraph [ref=e17]:
      - text: 还没有账号？
      - link "立即注册" [ref=e18] [cursor=pointer]:
        - /url: /register
  - alert [ref=e19]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('每日推送 - 已删除文章点击', () => {
  4  |   const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
  5  |   const USERNAME = process.env.USERNAME || 'admin';
  6  |   const PASSWORD = process.env.PASSWORD || 'password';
  7  | 
  8  |   test.beforeEach(async ({ page }) => {
  9  |     // 模拟文章详情接口返回404
  10 |     await page.route('**/api/articles/**', async route => {
  11 |       await route.fulfill({ status: 404, body: JSON.stringify({ error: '文章不存在' }) });
  12 |     });
  13 |     await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
> 14 |     await page.getByLabel('用户名').fill(USERNAME);
     |                                  ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  15 |     await page.getByLabel('密码').fill(PASSWORD);
  16 |     await page.getByRole('button', { name: '登录' }).click();
  17 |     await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  18 |   });
  19 | 
  20 |   test('验证点击已删除文章显示错误提示', async ({ page }) => {
  21 |     // 点击第一篇文章（假设后端将返回错误）
  22 |     await page.getByTestId('article-card').first().click();
  23 |     // 验证显示错误提示
  24 |     await expect(page.getByTestId('error-message')).toBeVisible();
  25 |     await expect(page.getByTestId('error-message')).toContainText('文章不存在');
  26 |   });
  27 | });
```