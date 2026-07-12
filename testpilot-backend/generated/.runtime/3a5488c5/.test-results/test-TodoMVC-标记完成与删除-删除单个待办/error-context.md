# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-标记完成与删除 >> 删除单个待办
- Location: testpilot-backend\generated\.runtime\3a5488c5\test.spec.ts:31:7

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  getByRole('listitem')
Expected: 2
Received: 5
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" with timeout 5000ms
  - waiting for getByRole('listitem')
    14 × locator resolved to 5 elements
       - unexpected value "5"

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
            - generic [ref=e16]: Task1
            - text: ×
        - listitem [ref=e17]:
          - generic [ref=e18]:
            - checkbox "Toggle Todo" [ref=e19]
            - generic [ref=e20]: Task3
            - button "Delete" [ref=e21]: ×
    - generic [ref=e22]:
      - generic [ref=e23]:
        - strong [ref=e24]: "2"
        - text: items left
      - list [ref=e25]:
        - listitem [ref=e26]:
          - link "All" [ref=e27] [cursor=pointer]:
            - /url: "#/"
        - listitem [ref=e28]:
          - link "Active" [ref=e29] [cursor=pointer]:
            - /url: "#/active"
        - listitem [ref=e30]:
          - link "Completed" [ref=e31] [cursor=pointer]:
            - /url: "#/completed"
  - contentinfo [ref=e32]:
    - paragraph [ref=e33]: Double-click to edit a todo
    - paragraph [ref=e34]:
      - text: Created by
      - link "Remo H. Jansen" [ref=e35] [cursor=pointer]:
        - /url: http://github.com/remojansen/
    - paragraph [ref=e36]:
      - text: Part of
      - link "TodoMVC" [ref=e37] [cursor=pointer]:
        - /url: http://todomvc.com
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-标记完成与删除', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |     const input = page.getByPlaceholder('What needs to be done?');
  7  |     await input.fill('Task1');
  8  |     await page.keyboard.press('Enter');
  9  |     await input.fill('Task2');
  10 |     await page.keyboard.press('Enter');
  11 |     await input.fill('Task3');
  12 |     await page.keyboard.press('Enter');
  13 |   });
  14 | 
  15 |   test('标记单个待办为完成', async ({ page }) => {
  16 |     const task1Checkbox = page.getByRole('listitem').filter({ hasText: 'Task1' }).getByRole('checkbox');
  17 |     await task1Checkbox.click();
  18 |     await expect(task1Checkbox).toBeChecked();
  19 |     await expect(page.getByText('2 items left')).toBeVisible();
  20 |   });
  21 | 
  22 |   test('取消标记完成', async ({ page }) => {
  23 |     const task1Checkbox = page.getByRole('listitem').filter({ hasText: 'Task1' }).getByRole('checkbox');
  24 |     await task1Checkbox.click();
  25 |     await expect(task1Checkbox).toBeChecked();
  26 |     await task1Checkbox.click();
  27 |     await expect(task1Checkbox).not.toBeChecked();
  28 |     await expect(page.getByText('3 items left')).toBeVisible();
  29 |   });
  30 | 
  31 |   test('删除单个待办', async ({ page }) => {
  32 |     const task2Item = page.getByRole('listitem').filter({ hasText: 'Task2' });
  33 |     await task2Item.hover();
  34 |     await task2Item.getByRole('button').click();
> 35 |     await expect(page.getByRole('listitem')).toHaveCount(2);
     |                                              ^ Error: expect(locator).toHaveCount(expected) failed
  36 |     await expect(page.getByText('2 items left')).toBeVisible();
  37 |   });
  38 | 
  39 |   test('清除所有已完成', async ({ page }) => {
  40 |     const task1Checkbox = page.getByRole('listitem').filter({ hasText: 'Task1' }).getByRole('checkbox');
  41 |     const task2Checkbox = page.getByRole('listitem').filter({ hasText: 'Task2' }).getByRole('checkbox');
  42 |     await task1Checkbox.click();
  43 |     await task2Checkbox.click();
  44 |     await page.getByRole('button', { name: 'Clear completed' }).click();
  45 |     await expect(page.getByRole('listitem')).toHaveCount(1);
  46 |     await expect(page.getByText('1 item left')).toBeVisible();
  47 |   });
  48 | });
```