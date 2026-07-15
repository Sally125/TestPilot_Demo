# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 每日推送 - 文章列表加载与展示 >> 验证文章列表正常加载并显示标题、摘要和发布时间
- Location: testpilot-backend\generated\.runtime\9508e186\test.spec.ts:17:7

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
  - generic [ref=e3]:
    - heading "404" [level=1] [ref=e4]
    - heading "This page could not be found." [level=2] [ref=e6]
  - alert [ref=e7]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('每日推送 - 文章列表加载与展示', () => {
  4  |   const BASE_URL = process.env.BASE_URL || 'http://localhost:3001/dashboard';
  5  |   const USERNAME = process.env.USERNAME || 'admin';
  6  |   const PASSWORD = process.env.PASSWORD || 'password';
  7  | 
  8  |   test.beforeEach(async ({ page }) => {
  9  |     // 登录
  10 |     await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
> 11 |     await page.getByLabel('用户名').fill(USERNAME);
     |                                  ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  12 |     await page.getByLabel('密码').fill(PASSWORD);
  13 |     await page.getByRole('button', { name: '登录' }).click();
  14 |     await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  15 |   });
  16 | 
  17 |   test('验证文章列表正常加载并显示标题、摘要和发布时间', async ({ page }) => {
  18 |     // 等待文章列表区域可见
  19 |     const articleList = page.getByTestId('article-list');
  20 |     await expect(articleList).toBeVisible();
  21 |     // 检查第一篇文章包含标题、摘要、发布时间
  22 |     const firstArticle = articleList.getByTestId('article-card').first();
  23 |     await expect(firstArticle).toBeVisible();
  24 |     await expect(firstArticle.getByTestId('article-title')).toBeVisible();
  25 |     await expect(firstArticle.getByTestId('article-summary')).toBeVisible();
  26 |     await expect(firstArticle.getByTestId('article-time')).toBeVisible();
  27 |     // 验证时间格式（简单检查日期模式）
  28 |     const timeText = await firstArticle.getByTestId('article-time').textContent();
  29 |     expect(timeText).toMatch(/\d{4}-\d{2}-\d{2}/);
  30 |   });
  31 | });
```