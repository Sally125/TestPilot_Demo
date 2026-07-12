# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-添加待办事项 >> 添加空输入不应新增待办
- Location: testpilot-backend\generated\.runtime\04173c78\test.spec.ts:13:7

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
  2  | test.describe('TodoMVC-添加待办事项', () => {
  3  |   test.beforeEach(async ({ page }) => {
  4  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  5  |   });
  6  |   test('正常添加待办事项', async ({ page }) => {
  7  |     const input = page.getByPlaceholder('What needs to be done?');
  8  |     await input.fill('测试待办');
  9  |     await input.press('Enter');
  10 |     await expect(page.getByText('测试待办')).toBeVisible();
  11 |     await expect(page.getByText(/1 item left/)).toBeVisible();
  12 |   });
  13 |   test('添加空输入不应新增待办', async ({ page }) => {
  14 |     const input = page.getByPlaceholder('What needs to be done?');
  15 |     await input.fill('');
  16 |     await input.press('Enter');
  17 |     await expect(page.getByRole('listitem')).toHaveCount(0);
> 18 |     await expect(page.getByText('0 items left')).toBeVisible();
     |                                                  ^ Error: expect(locator).toBeVisible() failed
  19 |   });
  20 |   test('添加纯空格输入不应新增待办', async ({ page }) => {
  21 |     const input = page.getByPlaceholder('What needs to be done?');
  22 |     await input.fill('   ');
  23 |     await input.press('Enter');
  24 |     await expect(page.getByRole('listitem')).toHaveCount(0);
  25 |     await expect(page.getByText('0 items left')).toBeVisible();
  26 |   });
  27 | });
```