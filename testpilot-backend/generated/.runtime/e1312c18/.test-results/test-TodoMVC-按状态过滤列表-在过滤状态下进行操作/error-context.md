# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-按状态过滤列表 >> 在过滤状态下进行操作
- Location: testpilot-backend\generated\.runtime\e1312c18\test.spec.ts:28:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.goto: Test timeout of 30000ms exceeded.
Call log:
  - navigating to "https://demo.playwright.dev/todomvc/", waiting until "domcontentloaded"

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - text: This is just a demo of TodoMVC for testing, not the
    - link "real TodoMVC app." [ref=e3] [cursor=pointer]:
      - /url: https://todomvc.com/
  - contentinfo [ref=e4]:
    - paragraph [ref=e5]: Double-click to edit a todo
    - paragraph [ref=e6]:
      - text: Created by
      - link "Remo H. Jansen" [ref=e7] [cursor=pointer]:
        - /url: http://github.com/remojansen/
    - paragraph [ref=e8]:
      - text: Part of
      - link "TodoMVC" [ref=e9] [cursor=pointer]:
        - /url: http://todomvc.com
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-按状态过滤列表', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: Test timeout of 30000ms exceeded.
  6  |     const input = page.getByPlaceholder('What needs to be done?');
  7  |     await input.fill('任务一');
  8  |     await input.press('Enter');
  9  |     await input.fill('任务二');
  10 |     await input.press('Enter');
  11 |     await input.fill('任务三');
  12 |     await input.press('Enter');
  13 |     await page.getByLabel('任务一').check();
  14 |   });
  15 | 
  16 |   test('按状态筛选列表', async ({ page }) => {
  17 |     await page.getByRole('link', { name: 'Active' }).click();
  18 |     await expect(page.locator('.todo-list li')).toHaveCount(2);
  19 |     await expect(page.getByText('任务二')).toBeVisible();
  20 |     await expect(page.getByText('任务三')).toBeVisible();
  21 |     await page.getByRole('link', { name: 'Completed' }).click();
  22 |     await expect(page.locator('.todo-list li')).toHaveCount(1);
  23 |     await expect(page.getByText('任务一')).toBeVisible();
  24 |     await page.getByRole('link', { name: 'All' }).click();
  25 |     await expect(page.locator('.todo-list li')).toHaveCount(3);
  26 |   });
  27 | 
  28 |   test('在过滤状态下进行操作', async ({ page }) => {
  29 |     await page.getByRole('link', { name: 'Active' }).click();
  30 |     await page.getByLabel('任务二').check();
  31 |     await expect(page.locator('.todo-list li')).toHaveCount(1);
  32 |     await expect(page.getByText('任务三')).toBeVisible();
  33 |     await page.getByRole('link', { name: 'Completed' }).click();
  34 |     await expect(page.locator('.todo-list li')).toHaveCount(2);
  35 |     const completedItem = page.locator('li', { hasText: '任务一' });
  36 |     await completedItem.hover();
  37 |     await completedItem.locator('button.destroy').click();
  38 |     await expect(page.locator('.todo-list li')).toHaveCount(1);
  39 |     await page.getByRole('link', { name: 'All' }).click();
  40 |     await expect(page.locator('.todo-list li')).toHaveCount(2);
  41 |   });
  42 | });
```