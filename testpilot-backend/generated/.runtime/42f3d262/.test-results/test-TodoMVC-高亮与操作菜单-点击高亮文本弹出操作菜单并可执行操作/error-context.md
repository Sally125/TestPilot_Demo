# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-高亮与操作菜单 >> 点击高亮文本弹出操作菜单并可执行操作
- Location: testpilot-backend\generated\.runtime\42f3d262\test.spec.ts:11:7

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
  3  | test.describe('TodoMVC-高亮与操作菜单', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('未提供', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
  6  |     // 进入精读页面
  7  |     await page.getByTestId('article-item').first().click();
  8  |     await expect(page.getByTestId('original-article-tab')).toBeVisible();
  9  |   });
  10 | 
  11 |   test('点击高亮文本弹出操作菜单并可执行操作', async ({ page }) => {
  12 |     // 点击一个高亮区域（假设为红色高亮）
  13 |     await page.getByTestId('highlight-red').first().click();
  14 |     await expect(page.getByTestId('operation-menu')).toBeVisible();
  15 |     await page.getByTestId('menu-copy').click();
  16 |     // 验证复制成功提示
  17 |     await expect(page.getByText(/复制成功|已复制/)).toBeVisible();
  18 |   });
  19 | 
  20 |   test('点击非高亮文本区域不弹出菜单', async ({ page }) => {
  21 |     // 点击一段普通文本
  22 |     await page.getByTestId('normal-text').first().click();
  23 |     await expect(page.getByTestId('operation-menu')).not.toBeVisible();
  24 |   });
  25 | });
```