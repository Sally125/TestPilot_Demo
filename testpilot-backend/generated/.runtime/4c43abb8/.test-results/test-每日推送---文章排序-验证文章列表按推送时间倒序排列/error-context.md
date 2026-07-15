# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 每日推送 - 文章排序 >> 验证文章列表按推送时间倒序排列
- Location: testpilot-backend\generated\.runtime\4c43abb8\test.spec.ts:16:7

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
  3  | test.describe('每日推送 - 文章排序', () => {
  4  |   const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
  5  |   const USERNAME = process.env.USERNAME || 'admin';
  6  |   const PASSWORD = process.env.PASSWORD || 'password';
  7  | 
  8  |   test.beforeEach(async ({ page }) => {
  9  |     await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
> 10 |     await page.getByLabel('用户名').fill(USERNAME);
     |                                  ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  11 |     await page.getByLabel('密码').fill(PASSWORD);
  12 |     await page.getByRole('button', { name: '登录' }).click();
  13 |     await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  14 |   });
  15 | 
  16 |   test('验证文章列表按推送时间倒序排列', async ({ page }) => {
  17 |     const articleList = page.getByTestId('article-list');
  18 |     await expect(articleList).toBeVisible();
  19 |     // 获取前两篇文章的发布时间
  20 |     const firstTime = await articleList.getByTestId('article-card').first().getByTestId('article-time').textContent();
  21 |     const secondTime = await articleList.getByTestId('article-card').nth(1).getByTestId('article-time').textContent();
  22 |     // 比较时间（假设时间字符串可直接比较，如'2025-03-10 10:00'）
  23 |     expect(new Date(firstTime).getTime()).toBeGreaterThan(new Date(secondTime).getTime());
  24 |   });
  25 | });
```