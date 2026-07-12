# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-添加待办与标记完成 >> 添加多个待办并全选/取消全选
- Location: testpilot-backend\generated\.runtime\00b1f1cb\test.spec.ts:38:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.goto: net::ERR_TIMED_OUT at https://demo.playwright.dev/todomvc/
Call log:
  - navigating to "https://demo.playwright.dev/todomvc/", waiting until "domcontentloaded"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-添加待办与标记完成', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: net::ERR_TIMED_OUT at https://demo.playwright.dev/todomvc/
  6  |   });
  7  | 
  8  |   test('正常添加待办并标记完成再取消', async ({ page }) => {
  9  |     // 添加待办
  10 |     const input = page.getByPlaceholder('What needs to be done?');
  11 |     await input.fill('测试待办');
  12 |     await input.press('Enter');
  13 |     // 验证待办出现
  14 |     const todoItem = page.getByTestId('todo-item').filter({ hasText: '测试待办' });
  15 |     await expect(todoItem).toBeVisible();
  16 |     // 验证未完成（没有 line-through）
  17 |     await expect(todoItem.locator('label')).not.toHaveCSS('text-decoration-line', 'line-through');
  18 |     // 标记完成
  19 |     await todoItem.getByRole('checkbox').check();
  20 |     await expect(todoItem.locator('label')).toHaveCSS('text-decoration-line', 'line-through');
  21 |     // 取消完成
  22 |     await todoItem.getByRole('checkbox').uncheck();
  23 |     await expect(todoItem.locator('label')).not.toHaveCSS('text-decoration-line', 'line-through');
  24 |   });
  25 | 
  26 |   test('输入空文本或仅空格时不应创建待办', async ({ page }) => {
  27 |     const input = page.getByPlaceholder('What needs to be done?');
  28 |     // 空文本
  29 |     await input.fill('');
  30 |     await input.press('Enter');
  31 |     await expect(page.getByTestId('todo-item')).not.toBeVisible();
  32 |     // 仅空格
  33 |     await input.fill('   ');
  34 |     await input.press('Enter');
  35 |     await expect(page.getByTestId('todo-item')).not.toBeVisible();
  36 |   });
  37 | 
  38 |   test('添加多个待办并全选/取消全选', async ({ page }) => {
  39 |     const input = page.getByPlaceholder('What needs to be done?');
  40 |     for (const text of ['任务1', '任务2', '任务3']) {
  41 |       await input.fill(text);
  42 |       await input.press('Enter');
  43 |     }
  44 |     // 全选
  45 |     await page.getByRole('checkbox', { name: 'Mark all as complete' }).check();
  46 |     await expect(page.getByTestId('todo-item').first().locator('label')).toHaveCSS('text-decoration-line', 'line-through');
  47 |     // 取消全选
  48 |     await page.getByRole('checkbox', { name: 'Mark all as complete' }).uncheck();
  49 |     await expect(page.getByTestId('todo-item').first().locator('label')).not.toHaveCSS('text-decoration-line', 'line-through');
  50 |   });
  51 | });
```