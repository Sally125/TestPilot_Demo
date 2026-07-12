# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-按状态过滤 >> 过滤显示已完成（Completed）
- Location: testpilot-backend\generated\.runtime\55dec07c\test.spec.ts:25:7

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
- generic [ref=e1]:
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
            - checkbox "Toggle Todo" [checked] [ref=e15]
            - generic [ref=e16]: Task1
            - text: ×
    - generic [ref=e17]:
      - generic [ref=e18]:
        - strong [ref=e19]: "2"
        - text: items left
      - list [ref=e20]:
        - listitem [ref=e21]:
          - link "All" [ref=e22] [cursor=pointer]:
            - /url: "#/"
        - listitem [ref=e23]:
          - link "Active" [ref=e24] [cursor=pointer]:
            - /url: "#/active"
        - listitem [ref=e25]:
          - link "Completed" [active] [ref=e26] [cursor=pointer]:
            - /url: "#/completed"
      - button "Clear completed" [ref=e27] [cursor=pointer]
  - contentinfo [ref=e28]:
    - paragraph [ref=e29]: Double-click to edit a todo
    - paragraph [ref=e30]:
      - text: Created by
      - link "Remo H. Jansen" [ref=e31] [cursor=pointer]:
        - /url: http://github.com/remojansen/
    - paragraph [ref=e32]:
      - text: Part of
      - link "TodoMVC" [ref=e33] [cursor=pointer]:
        - /url: http://todomvc.com
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-按状态过滤', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |     const input = page.getByPlaceholder('What needs to be done?');
  7  |     await input.fill('Task1');
  8  |     await page.keyboard.press('Enter');
  9  |     await input.fill('Task2');
  10 |     await page.keyboard.press('Enter');
  11 |     await input.fill('Task3');
  12 |     await page.keyboard.press('Enter');
  13 |     await page.getByRole('listitem').filter({ hasText: 'Task1' }).getByRole('checkbox').click();
  14 |   });
  15 | 
  16 |   test('过滤显示待办（Active）', async ({ page }) => {
  17 |     await page.getByRole('link', { name: 'Active' }).click();
  18 |     await expect(page.getByRole('listitem')).toHaveCount(2);
  19 |     await expect(page.getByText('Task1')).toBeHidden();
  20 |     await expect(page.getByText('Task2')).toBeVisible();
  21 |     await expect(page.getByText('Task3')).toBeVisible();
  22 |     await expect(page.getByText('2 items left')).toBeVisible();
  23 |   });
  24 | 
  25 |   test('过滤显示已完成（Completed）', async ({ page }) => {
  26 |     await page.getByRole('link', { name: 'Completed' }).click();
> 27 |     await expect(page.getByRole('listitem')).toHaveCount(1);
     |                                              ^ Error: expect(locator).toHaveCount(expected) failed
  28 |     await expect(page.getByText('Task1')).toBeVisible();
  29 |     await expect(page.getByText('Task2')).toBeHidden();
  30 |     await expect(page.getByText('2 items left')).toBeVisible();
  31 |   });
  32 | 
  33 |   test('显示所有待办（All）', async ({ page }) => {
  34 |     await page.getByRole('link', { name: 'All' }).click();
  35 |     await expect(page.getByRole('listitem')).toHaveCount(3);
  36 |     await expect(page.getByText('Task1')).toBeVisible();
  37 |     await expect(page.getByText('Task2')).toBeVisible();
  38 |     await expect(page.getByText('Task3')).toBeVisible();
  39 |     await expect(page.getByText('2 items left')).toBeVisible();
  40 |   });
  41 | 
  42 |   test('在过滤状态下标记完成', async ({ page }) => {
  43 |     await page.getByRole('link', { name: 'Active' }).click();
  44 |     const task2Checkbox = page.getByRole('listitem').filter({ hasText: 'Task2' }).getByRole('checkbox');
  45 |     await task2Checkbox.click();
  46 |     await expect(page.getByRole('listitem')).toHaveCount(1);
  47 |     await expect(page.getByText('Task2')).toBeHidden();
  48 |     await expect(page.getByText('Task3')).toBeVisible();
  49 |   });
  50 | });
```