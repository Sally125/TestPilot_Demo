# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-标记完成与删除 >> 批量清除已完成待办
- Location: testpilot-backend\generated\.runtime\4bfb0aac\test.spec.ts:34:7

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  getByRole('listitem')
Expected: 1
Received: 4
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" with timeout 5000ms
  - waiting for getByRole('listitem')
    14 × locator resolved to 4 elements
       - unexpected value "4"

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - text: This is just a demo of TodoMVC for testing, not the
    - link "real TodoMVC app." [ref=e3] [cursor=pointer]:
      - /url: https://todomvc.com/
  - generic [ref=e5]:
    - generic [ref=e6]:
      - heading "todos" [level=1] [ref=e7]
      - textbox "What needs to be done?" [ref=e8]
    - generic [ref=e9]:
      - checkbox "❯Mark all as complete" [ref=e10]
      - generic [ref=e11]: ❯Mark all as complete
      - list [ref=e12]:
        - listitem [ref=e13]:
          - generic [ref=e14]:
            - checkbox "Toggle Todo" [ref=e15]
            - generic [ref=e16]: 运动
            - text: ×
    - generic [ref=e17]:
      - generic [ref=e18]:
        - strong [ref=e19]: "1"
        - text: item left
      - list [ref=e20]:
        - listitem [ref=e21]:
          - link "All" [ref=e22] [cursor=pointer]:
            - /url: "#/"
        - listitem [ref=e23]:
          - link "Active" [ref=e24] [cursor=pointer]:
            - /url: "#/active"
        - listitem [ref=e25]:
          - link "Completed" [ref=e26] [cursor=pointer]:
            - /url: "#/completed"
  - contentinfo [ref=e27]:
    - paragraph [ref=e28]: Double-click to edit a todo
    - paragraph [ref=e29]:
      - text: Created by
      - link "Remo H. Jansen" [ref=e30] [cursor=pointer]:
        - /url: http://github.com/remojansen/
    - paragraph [ref=e31]:
      - text: Part of
      - link "TodoMVC" [ref=e32] [cursor=pointer]:
        - /url: http://todomvc.com
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-标记完成与删除', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |     await page.evaluate(() => localStorage.clear());
  7  |     await page.reload({ waitUntil: 'domcontentloaded' });
  8  |   });
  9  | 
  10 |   test('标记待办完成并取消完成', async ({ page }) => {
  11 |     const todoText1 = '任务一';
  12 |     const todoText2 = '任务二';
  13 |     await page.getByPlaceholder('What needs to be done?').fill(todoText1);
  14 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  15 |     await page.getByPlaceholder('What needs to be done?').fill(todoText2);
  16 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  17 |     const firstCheckbox = page.getByRole('listitem').filter({ hasText: todoText1 }).getByRole('checkbox');
  18 |     await firstCheckbox.check();
  19 |     await expect(firstCheckbox).toBeChecked();
  20 |     await firstCheckbox.uncheck();
  21 |     await expect(firstCheckbox).not.toBeChecked();
  22 |   });
  23 | 
  24 |   test('删除单个待办', async ({ page }) => {
  25 |     const todoText = '待删除任务';
  26 |     await page.getByPlaceholder('What needs to be done?').fill(todoText);
  27 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  28 |     const todoItem = page.getByRole('listitem').filter({ hasText: todoText });
  29 |     await todoItem.hover();
  30 |     await todoItem.locator('.destroy').click();
  31 |     await expect(page.getByText(todoText)).not.toBeVisible();
  32 |   });
  33 | 
  34 |   test('批量清除已完成待办', async ({ page }) => {
  35 |     const todos = ['读书', '写作', '运动'];
  36 |     for (const text of todos) {
  37 |       await page.getByPlaceholder('What needs to be done?').fill(text);
  38 |       await page.getByPlaceholder('What needs to be done?').press('Enter');
  39 |     }
  40 |     await page.getByRole('listitem').filter({ hasText: todos[0] }).getByRole('checkbox').check();
  41 |     await page.getByRole('listitem').filter({ hasText: todos[1] }).getByRole('checkbox').check();
  42 |     await page.getByRole('button', { name: 'Clear completed' }).click();
> 43 |     await expect(page.getByRole('listitem')).toHaveCount(1);
     |                                              ^ Error: expect(locator).toHaveCount(expected) failed
  44 |     await expect(page.getByText(todos[2])).toBeVisible();
  45 |     await expect(page.getByText(todos[0])).not.toBeVisible();
  46 |     await expect(page.getByText(todos[1])).not.toBeVisible();
  47 |     await expect(page.getByText('1 item left')).toBeVisible();
  48 |   });
  49 | });
```