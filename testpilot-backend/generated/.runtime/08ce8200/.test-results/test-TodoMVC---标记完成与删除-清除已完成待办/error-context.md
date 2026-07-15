# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC - 标记完成与删除 >> 清除已完成待办
- Location: testpilot-backend\generated\.runtime\08ce8200\test.spec.ts:36:7

# Error details

```
Error: locator.check: Error: strict mode violation: getByRole('listitem').filter({ hasText: '完成项' }).getByRole('checkbox') resolved to 2 elements:
    1) <input class="toggle" type="checkbox" aria-label="Toggle Todo"/> aka getByRole('checkbox', { name: 'Toggle Todo' }).first()
    2) <input class="toggle" type="checkbox" aria-label="Toggle Todo"/> aka getByRole('listitem').filter({ hasText: '未完成项' }).getByLabel('Toggle Todo')

Call log:
  - waiting for getByRole('listitem').filter({ hasText: '完成项' }).getByRole('checkbox')

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
      - textbox "What needs to be done?" [active] [ref=e8]
    - generic [ref=e9]:
      - checkbox "❯Mark all as complete" [ref=e10]
      - generic [ref=e11]: ❯Mark all as complete
      - list [ref=e12]:
        - listitem [ref=e13]:
          - generic [ref=e14]:
            - checkbox "Toggle Todo" [ref=e15]
            - generic [ref=e16]: 完成项
            - text: ×
        - listitem [ref=e17]:
          - generic [ref=e18]:
            - checkbox "Toggle Todo" [ref=e19]
            - generic [ref=e20]: 未完成项
            - text: ×
    - generic [ref=e21]:
      - generic [ref=e22]:
        - strong [ref=e23]: "2"
        - text: items left
      - list [ref=e24]:
        - listitem [ref=e25]:
          - link "All" [ref=e26] [cursor=pointer]:
            - /url: "#/"
        - listitem [ref=e27]:
          - link "Active" [ref=e28] [cursor=pointer]:
            - /url: "#/active"
        - listitem [ref=e29]:
          - link "Completed" [ref=e30] [cursor=pointer]:
            - /url: "#/completed"
  - contentinfo [ref=e31]:
    - paragraph [ref=e32]: Double-click to edit a todo
    - paragraph [ref=e33]:
      - text: Created by
      - link "Remo H. Jansen" [ref=e34] [cursor=pointer]:
        - /url: http://github.com/remojansen/
    - paragraph [ref=e35]:
      - text: Part of
      - link "TodoMVC" [ref=e36] [cursor=pointer]:
        - /url: http://todomvc.com
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC - 标记完成与删除', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |   });
  7  | 
  8  |   test('标记完成和取消完成', async ({ page }) => {
  9  |     const input = page.getByPlaceholder('What needs to be done?');
  10 |     await input.fill('任务A');
  11 |     await input.press('Enter');
  12 |     await input.fill('任务B');
  13 |     await input.press('Enter');
  14 | 
  15 |     const taskA = page.getByRole('listitem').filter({ hasText: '任务A' });
  16 |     const checkbox = taskA.getByRole('checkbox');
  17 |     await checkbox.check();
  18 |     await expect(checkbox).toBeChecked();
  19 |     await expect(taskA).toHaveClass(/completed/);
  20 |     await checkbox.uncheck();
  21 |     await expect(checkbox).not.toBeChecked();
  22 |     await expect(taskA).not.toHaveClass(/completed/);
  23 |   });
  24 | 
  25 |   test('删除单个待办', async ({ page }) => {
  26 |     const input = page.getByPlaceholder('What needs to be done?');
  27 |     await input.fill('待删除');
  28 |     await input.press('Enter');
  29 | 
  30 |     const item = page.getByRole('listitem').filter({ hasText: '待删除' });
  31 |     await item.hover();
  32 |     await item.getByRole('button').click();
  33 |     await expect(item).not.toBeVisible();
  34 |   });
  35 | 
  36 |   test('清除已完成待办', async ({ page }) => {
  37 |     const input = page.getByPlaceholder('What needs to be done?');
  38 |     await input.fill('完成项');
  39 |     await input.press('Enter');
  40 |     await input.fill('未完成项');
  41 |     await input.press('Enter');
  42 | 
  43 |     const completedItem = page.getByRole('listitem').filter({ hasText: '完成项' });
> 44 |     await completedItem.getByRole('checkbox').check();
     |                                               ^ Error: locator.check: Error: strict mode violation: getByRole('listitem').filter({ hasText: '完成项' }).getByRole('checkbox') resolved to 2 elements:
  45 | 
  46 |     const clearButton = page.getByRole('button', { name: 'Clear completed' });
  47 |     await clearButton.click();
  48 | 
  49 |     await expect(page.getByText('完成项')).not.toBeVisible();
  50 |     await expect(page.getByText('未完成项')).toBeVisible();
  51 |   });
  52 | });
```