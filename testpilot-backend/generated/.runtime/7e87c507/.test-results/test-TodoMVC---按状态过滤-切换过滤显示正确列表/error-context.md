# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC - 按状态过滤 >> 切换过滤显示正确列表
- Location: testpilot-backend\generated\.runtime\7e87c507\test.spec.ts:8:7

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
            - checkbox "Toggle Todo" [ref=e15]
            - generic [ref=e16]: 待办3
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
          - link "Active" [active] [ref=e24] [cursor=pointer]:
            - /url: "#/active"
        - listitem [ref=e25]:
          - link "Completed" [ref=e26] [cursor=pointer]:
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
  3  | test.describe('TodoMVC - 按状态过滤', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |   });
  7  | 
  8  |   test('切换过滤显示正确列表', async ({ page }) => {
  9  |     const input = page.getByPlaceholder('What needs to be done?');
  10 |     await input.fill('待办1');
  11 |     await input.press('Enter');
  12 |     await input.fill('待办2');
  13 |     await input.press('Enter');
  14 |     await input.fill('待办3');
  15 |     await input.press('Enter');
  16 | 
  17 |     // 完成待办1和待办2
  18 |     const item1 = page.getByRole('listitem').filter({ hasText: '待办1' });
  19 |     const item2 = page.getByRole('listitem').filter({ hasText: '待办2' });
  20 |     await item1.getByRole('checkbox').check();
  21 |     await item2.getByRole('checkbox').check();
  22 | 
  23 |     // 点击 Active
  24 |     await page.getByRole('link', { name: 'Active' }).click();
> 25 |     await expect(page.getByRole('listitem')).toHaveCount(1);
     |                                              ^ Error: expect(locator).toHaveCount(expected) failed
  26 |     await expect(page.getByText('待办3')).toBeVisible();
  27 | 
  28 |     // 点击 Completed
  29 |     await page.getByRole('link', { name: 'Completed' }).click();
  30 |     await expect(page.getByRole('listitem')).toHaveCount(2);
  31 |   });
  32 | 
  33 |   test('过滤状态下操作', async ({ page }) => {
  34 |     const input = page.getByPlaceholder('What needs to be done?');
  35 |     await input.fill('任务1');
  36 |     await input.press('Enter');
  37 |     await input.fill('任务2');
  38 |     await input.press('Enter');
  39 | 
  40 |     // 完成任务1
  41 |     const task1 = page.getByRole('listitem').filter({ hasText: '任务1' });
  42 |     await task1.getByRole('checkbox').check();
  43 | 
  44 |     // 切换到 Active
  45 |     await page.getByRole('link', { name: 'Active' }).click();
  46 |     await expect(page.getByRole('listitem')).toHaveCount(1);
  47 |     await expect(page.getByText('任务2')).toBeVisible();
  48 | 
  49 |     // 在 Active 下完成任务2
  50 |     const task2 = page.getByRole('listitem').filter({ hasText: '任务2' });
  51 |     await task2.getByRole('checkbox').check();
  52 | 
  53 |     // Active 列表为空
  54 |     await expect(page.getByRole('listitem')).toHaveCount(0);
  55 | 
  56 |     // 切换到 Completed 应看到两个任务
  57 |     await page.getByRole('link', { name: 'Completed' }).click();
  58 |     await expect(page.getByRole('listitem')).toHaveCount(2);
  59 |   });
  60 | });
```