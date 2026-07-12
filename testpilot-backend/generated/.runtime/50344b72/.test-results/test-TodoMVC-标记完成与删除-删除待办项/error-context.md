# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-标记完成与删除 >> 删除待办项
- Location: testpilot-backend\generated\.runtime\50344b72\test.spec.ts:22:7

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
  3  | test.describe('TodoMVC-标记完成与删除', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: Test timeout of 30000ms exceeded.
  6  |     const input = page.getByPlaceholder('What needs to be done?');
  7  |     await input.fill('待办一');
  8  |     await input.press('Enter');
  9  |     await input.fill('待办二');
  10 |     await input.press('Enter');
  11 |     await input.fill('待办三');
  12 |     await input.press('Enter');
  13 |   });
  14 | 
  15 |   test('标记完成并取消完成', async ({ page }) => {
  16 |     await page.getByLabel('待办二').check();
  17 |     await expect(page.getByText('待办二')).toHaveClass(/completed/);
  18 |     await page.getByLabel('待办二').uncheck();
  19 |     await expect(page.getByText('待办二')).not.toHaveClass(/completed/);
  20 |   });
  21 | 
  22 |   test('删除待办项', async ({ page }) => {
  23 |     const todoItem = page.locator('li', { hasText: '待办一' });
  24 |     await todoItem.hover();
  25 |     await todoItem.locator('button.destroy').click();
  26 |     await expect(page.getByText('待办一')).toHaveCount(0);
  27 |     await expect(page.locator('.todo-count')).toHaveText('2 items left');
  28 |   });
  29 | 
  30 |   test('清除已完成的待办', async ({ page }) => {
  31 |     await page.getByLabel('待办一').check();
  32 |     await page.getByLabel('待办二').check();
  33 |     await page.getByText('Clear completed').click();
  34 |     await expect(page.locator('.todo-list li')).toHaveCount(1);
  35 |     await expect(page.getByText('待办三')).toBeVisible();
  36 |     await expect(page.locator('.todo-count')).toHaveText('1 item left');
  37 |   });
  38 | });
```