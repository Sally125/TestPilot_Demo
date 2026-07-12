# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-添加待办 >> 正常添加待办
- Location: testpilot-backend\generated\.runtime\1b393f65\test.spec.ts:8:7

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
  3  | test.describe('TodoMVC-添加待办', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: Test timeout of 30000ms exceeded.
  6  |   });
  7  | 
  8  |   test('正常添加待办', async ({ page }) => {
  9  |     const todoText = '学习Playwright';
  10 |     await page.getByPlaceholder('What needs to be done?').fill(todoText);
  11 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  12 |     await expect(page.locator('ul.todo-list li').filter({ hasText: todoText })).toBeVisible();
  13 |     await expect(page.locator('.todo-count')).toHaveText('1 item left');
  14 |   });
  15 | 
  16 |   test('添加空文本不应创建待办', async ({ page }) => {
  17 |     await page.getByPlaceholder('What needs to be done?').fill('已有待办');
  18 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  19 |     await expect(page.locator('ul.todo-list li')).toHaveCount(1);
  20 | 
  21 |     await page.getByPlaceholder('What needs to be done?').fill('');
  22 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  23 |     await expect(page.locator('ul.todo-list li')).toHaveCount(1);
  24 | 
  25 |     await page.getByPlaceholder('What needs to be done?').fill('   ');
  26 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  27 |     await expect(page.locator('ul.todo-list li')).toHaveCount(1);
  28 |   });
  29 | 
  30 |   test('添加特殊字符待办', async ({ page }) => {
  31 |     const specialText = '<script>alert("xss")</script>';
  32 |     await page.getByPlaceholder('What needs to be done?').fill(specialText);
  33 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  34 |     await expect(page.locator('ul.todo-list li').filter({ hasText: specialText })).toBeVisible();
  35 |   });
  36 | });
```