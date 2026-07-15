# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-文章浏览与精读 >> 正常浏览文章列表并进入精读页
- Location: testpilot-backend\generated\.runtime\dcea5293\test.spec.ts:8:7

# Error details

```
Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
Call log:
  - navigating to "未提供", waiting until "domcontentloaded"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-文章浏览与精读', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('未提供', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
  6  |   });
  7  | 
  8  |   test('正常浏览文章列表并进入精读页', async ({ page }) => {
  9  |     await expect(page.getByTestId('article-list')).toBeVisible({ timeout: 10000 });
  10 |     await page.getByTestId('article-item').first().click();
  11 |     await expect(page.getByTestId('original-article-tab')).toBeVisible();
  12 |     await page.getByTestId('deconstruction-tab').click();
  13 |     await expect(page.getByTestId('deconstruction-content')).toBeVisible();
  14 |   });
  15 | 
  16 |   test('文章列表为空时显示提示信息', async ({ page }) => {
  17 |     await expect(page.getByText('暂无推送文章')).toBeVisible({ timeout: 5000 });
  18 |   });
  19 | });
```