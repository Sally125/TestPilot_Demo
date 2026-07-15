# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-添加待办 >> 空输入不添加待办
- Location: testpilot-backend\generated\.runtime\ac5c581b\test.spec.ts:16:7

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
  2  | 
  3  | test.describe('TodoMVC-添加待办', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |   });
  7  | 
  8  |   test('正常添加待办', async ({ page }) => {
  9  |     const input = page.getByPlaceholder('What needs to be done?');
  10 |     await input.fill('学习 Playwright');
  11 |     await input.press('Enter');
  12 |     await expect(page.getByText('学习 Playwright')).toBeVisible();
  13 |     await expect(page.getByText('1 item left')).toBeVisible();
  14 |   });
  15 | 
  16 |   test('空输入不添加待办', async ({ page }) => {
  17 |     const input = page.getByPlaceholder('What needs to be done?');
  18 |     await input.fill('');
  19 |     await input.press('Enter');
> 20 |     await expect(page.getByText('0 items left')).toBeVisible();
     |                                                  ^ Error: expect(locator).toBeVisible() failed
  21 |     // 通过计数确保没有新增，也可检查列表项数量
  22 |   });
  23 | });
```