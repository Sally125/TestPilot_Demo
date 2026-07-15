# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 每日推送 - 加载状态 >> 验证文章列表加载时显示加载状态
- Location: testpilot-backend\generated\.runtime\bf2975f5\test.spec.ts:21:7

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
  3  | test.describe('每日推送 - 加载状态', () => {
  4  |   const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
  5  |   const USERNAME = process.env.USERNAME || 'admin';
  6  |   const PASSWORD = process.env.PASSWORD || 'password';
  7  | 
  8  |   test.beforeEach(async ({ page }) => {
  9  |     // 模拟文章接口延迟，确保加载指示器可见
  10 |     await page.route('**/api/articles**', async route => {
  11 |       await new Promise(resolve => setTimeout(resolve, 2000)); // 延迟2秒
  12 |       await route.continue();
  13 |     });
  14 |     await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
> 15 |     await page.getByLabel('用户名').fill(USERNAME);
     |                                  ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  16 |     await page.getByLabel('密码').fill(PASSWORD);
  17 |     await page.getByRole('button', { name: '登录' }).click();
  18 |     await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  19 |   });
  20 | 
  21 |   test('验证文章列表加载时显示加载状态', async ({ page }) => {
  22 |     // 检查加载指示器出现
  23 |     const loadingIndicator = page.getByTestId('loading-indicator');
  24 |     await expect(loadingIndicator).toBeVisible();
  25 |     // 等待加载完成，指示器消失
  26 |     await expect(loadingIndicator).not.toBeVisible({ timeout: 10000 });
  27 |     // 文章列表可见
  28 |     await expect(page.getByTestId('article-list')).toBeVisible();
  29 |   });
  30 | });
```