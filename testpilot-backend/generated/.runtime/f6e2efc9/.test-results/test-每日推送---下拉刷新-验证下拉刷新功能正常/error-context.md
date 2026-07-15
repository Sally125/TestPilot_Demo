# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 每日推送 - 下拉刷新 >> 验证下拉刷新功能正常
- Location: testpilot-backend\generated\.runtime\f6e2efc9\test.spec.ts:16:7

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
  3  | test.describe('每日推送 - 下拉刷新', () => {
  4  |   const BASE_URL = process.env.BASE_URL || 'http://localhost:3001/dashboard';
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
  16 |   test('验证下拉刷新功能正常', async ({ page }) => {
  17 |     // 模拟后端新增一篇文章：通过route在刷新时返回新数据
  18 |     await page.route('**/api/articles*', async route => {
  19 |       // 每次刷新返回包含新文章的列表
  20 |       const articles = [
  21 |         { id: 99, title: '最新文章', summary: '新摘要', time: '2025-03-11' },
  22 |         { id: 1, title: '原有文章', summary: '旧摘要', time: '2025-03-10' }
  23 |       ];
  24 |       await route.fulfill({ status: 200, body: JSON.stringify({ articles, hasMore: false }) });
  25 |     });
  26 |     // 执行下拉刷新（假设通过点击刷新按钮或手势）
  27 |     const refreshButton = page.getByTestId('refresh-button');
  28 |     if (await refreshButton.isVisible()) {
  29 |       await refreshButton.click();
  30 |     } else {
  31 |       // 模拟下拉手势（需在移动端或通过touch事件）
  32 |       await page.evaluate(() => {
  33 |         const element = document.querySelector('[data-testid="article-list"]');
  34 |         if(element) {
  35 |           const startY = 0;
  36 |           const endY = 300;
  37 |           const startEvent = new TouchEvent('touchstart', { touches: [{ clientX: 0, clientY: startY }] });
  38 |           const moveEvent = new TouchEvent('touchmove', { touches: [{ clientX: 0, clientY: endY }] });
  39 |           const endEvent = new TouchEvent('touchend', { changes: [{ clientX: 0, clientY: endY }] });
  40 |           element.dispatchEvent(startEvent);
  41 |           element.dispatchEvent(moveEvent);
  42 |           element.dispatchEvent(endEvent);
  43 |         }
  44 |       });
  45 |     }
  46 |     // 等待刷新完成，新文章出现在列表最上方
  47 |     const firstArticle = page.getByTestId('article-card').first();
  48 |     await expect(firstArticle.getByTestId('article-title')).toHaveText('最新文章');
  49 |   });
  50 | });
```