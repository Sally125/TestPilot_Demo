# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-删除待办事项 >> 删除所有待办项
- Location: testpilot-backend\generated\.runtime\9400b345\test.spec.ts:18:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('0 items left')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('0 items left')

```

```yaml
- text: This is just a demo of TodoMVC for testing, not the
- link "real TodoMVC app.":
  - /url: https://todomvc.com/
- heading "todos" [level=1]
- textbox "What needs to be done?"
- contentinfo:
  - paragraph: Double-click to edit a todo
  - paragraph:
    - text: Created by
    - link "Remo H. Jansen":
      - /url: http://github.com/remojansen/
  - paragraph:
    - text: Part of
    - link "TodoMVC":
      - /url: http://todomvc.com
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | test.describe('TodoMVC-删除待办事项', () => {
  3  |   test.beforeEach(async ({ page }) => {
  4  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  5  |     const input = page.getByPlaceholder('What needs to be done?');
  6  |     await input.fill('待办一');
  7  |     await input.press('Enter');
  8  |     await input.fill('待办二');
  9  |     await input.press('Enter');
  10 |   });
  11 |   test('删除一个待办项', async ({ page }) => {
  12 |     const todoItem = page.getByRole('listitem').filter({ hasText: '待办一' });
  13 |     await todoItem.hover();
  14 |     await todoItem.locator('button').click();
  15 |     await expect(page.getByText('待办一')).not.toBeVisible();
  16 |     await expect(page.getByText('1 item left')).toBeVisible();
  17 |   });
  18 |   test('删除所有待办项', async ({ page }) => {
  19 |     const item1 = page.getByRole('listitem').filter({ hasText: '待办一' });
  20 |     await item1.hover();
  21 |     await item1.locator('button').click();
  22 |     const item2 = page.getByRole('listitem').filter({ hasText: '待办二' });
  23 |     await item2.hover();
  24 |     await item2.locator('button').click();
  25 |     await expect(page.getByRole('listitem')).toHaveCount(0);
> 26 |     await expect(page.getByText('0 items left')).toBeVisible();
     |                                                  ^ Error: expect(locator).toBeVisible() failed
  27 |   });
  28 | });
```