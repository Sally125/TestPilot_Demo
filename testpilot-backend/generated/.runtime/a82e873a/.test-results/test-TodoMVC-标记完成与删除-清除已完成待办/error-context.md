# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-标记完成与删除 >> 清除已完成待办
- Location: testpilot-backend\generated\.runtime\a82e873a\test.spec.ts:34:7

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator: locator('.todo-count')
Expected: "0 items left"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toHaveText" with timeout 5000ms
  - waiting for locator('.todo-count')

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
  3  | test.describe('TodoMVC-标记完成与删除', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |     await page.getByPlaceholder('What needs to be done?').fill('待办A');
  7  |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  8  |     await page.getByPlaceholder('What needs to be done?').fill('待办B');
  9  |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  10 |     await expect(page.locator('ul.todo-list li')).toHaveCount(2);
  11 |   });
  12 | 
  13 |   test('标记完成与取消完成', async ({ page }) => {
  14 |     const todoA = page.locator('li').filter({ hasText: '待办A' });
  15 |     const checkbox = todoA.locator('input[type="checkbox"]');
  16 |     await checkbox.click();
  17 |     await expect(checkbox).toBeChecked();
  18 |     await expect(page.locator('.todo-count')).toHaveText('1 item left');
  19 |     await checkbox.click();
  20 |     await expect(checkbox).not.toBeChecked();
  21 |     await expect(page.locator('.todo-count')).toHaveText('2 items left');
  22 |   });
  23 | 
  24 |   test('删除单条待办', async ({ page }) => {
  25 |     const todoB = page.locator('li').filter({ hasText: '待办B' });
  26 |     await todoB.hover();
  27 |     const deleteButton = todoB.locator('button.destroy');
  28 |     await deleteButton.click();
  29 |     await expect(todoB).not.toBeVisible();
  30 |     await expect(page.locator('ul.todo-list li')).toHaveCount(1);
  31 |     await expect(page.locator('.todo-count')).toHaveText('1 item left');
  32 |   });
  33 | 
  34 |   test('清除已完成待办', async ({ page }) => {
  35 |     const todoA = page.locator('li').filter({ hasText: '待办A' });
  36 |     await todoA.locator('input[type="checkbox"]').click();
  37 |     const todoB = page.locator('li').filter({ hasText: '待办B' });
  38 |     await todoB.locator('input[type="checkbox"]').click();
  39 |     await page.getByRole('button', { name: 'Clear completed' }).click();
  40 |     await expect(page.locator('ul.todo-list li')).toHaveCount(0);
> 41 |     await expect(page.locator('.todo-count')).toHaveText('0 items left');
     |                                               ^ Error: expect(locator).toHaveText(expected) failed
  42 |   });
  43 | });
```