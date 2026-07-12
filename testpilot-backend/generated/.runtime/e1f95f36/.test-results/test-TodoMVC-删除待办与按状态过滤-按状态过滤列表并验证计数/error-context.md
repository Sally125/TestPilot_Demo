# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-删除待办与按状态过滤 >> 按状态过滤列表并验证计数
- Location: testpilot-backend\generated\.runtime\e1f95f36\test.spec.ts:25:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('3 items left')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('3 items left')

```

```yaml
- text: This is just a demo of TodoMVC for testing, not the
- link "real TodoMVC app.":
  - /url: https://todomvc.com/
- heading "todos" [level=1]
- textbox "What needs to be done?"
- checkbox "❯Mark all as complete"
- text: ❯Mark all as complete
- list:
  - listitem:
    - checkbox "Toggle Todo"
    - text: 任务A
  - listitem:
    - checkbox "Toggle Todo" [checked]
    - text: 任务B
    - button "Delete": ×
  - listitem:
    - checkbox "Toggle Todo"
    - text: 任务C
- strong: "2"
- text: items left
- list:
  - listitem:
    - link "All":
      - /url: "#/"
  - listitem:
    - link "Active":
      - /url: "#/active"
  - listitem:
    - link "Completed":
      - /url: "#/completed"
- button "Clear completed"
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
  3  | test.describe('TodoMVC-删除待办与按状态过滤', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |     // 添加三个待办，并标记第二个为已完成
  7  |     const input = page.getByPlaceholder('What needs to be done?');
  8  |     for (const text of ['任务A', '任务B', '任务C']) {
  9  |       await input.fill(text);
  10 |       await input.press('Enter');
  11 |     }
  12 |     // 标记任务B为完成
  13 |     await page.getByTestId('todo-item').filter({ hasText: '任务B' }).getByRole('checkbox').check();
  14 |   });
  15 | 
  16 |   test('删除单个待办', async ({ page }) => {
  17 |     const todo = page.getByTestId('todo-item').filter({ hasText: '任务A' });
  18 |     await expect(todo).toBeVisible();
  19 |     // 悬停后点击删除按钮
  20 |     await todo.hover();
  21 |     await todo.locator('button.destroy').click();
  22 |     await expect(todo).not.toBeVisible();
  23 |   });
  24 | 
  25 |   test('按状态过滤列表并验证计数', async ({ page }) => {
  26 |     // 验证初始计数显示 3 items left
> 27 |     await expect(page.getByText('3 items left')).toBeVisible();
     |                                                  ^ Error: expect(locator).toBeVisible() failed
  28 |     // 点击「已完成」
  29 |     await page.getByRole('link', { name: 'Completed' }).click();
  30 |     await expect(page.getByTestId('todo-item')).toHaveCount(1);
  31 |     await expect(page.getByTestId('todo-item').filter({ hasText: '任务B' })).toBeVisible();
  32 |     await expect(page.getByText('3 items left')).not.toBeVisible();
  33 |     // 点击「待办」
  34 |     await page.getByRole('link', { name: 'Active' }).click();
  35 |     await expect(page.getByTestId('todo-item')).toHaveCount(2);
  36 |     await expect(page.getByTestId('todo-item').filter({ hasText: '任务A' })).toBeVisible();
  37 |     // 点击「所有」
  38 |     await page.getByRole('link', { name: 'All' }).click();
  39 |     await expect(page.getByTestId('todo-item')).toHaveCount(3);
  40 |   });
  41 | 
  42 |   test('清除所有已完成待办', async ({ page }) => {
  43 |     // 点击清除已完成按钮
  44 |     await page.getByRole('button', { name: 'Clear completed' }).click();
  45 |     await expect(page.getByTestId('todo-item')).toHaveCount(2);
  46 |     await expect(page.getByTestId('todo-item').filter({ hasText: '任务B' })).not.toBeVisible();
  47 |     // 验证底部计数更新
  48 |     await expect(page.getByText('2 items left')).toBeVisible();
  49 |   });
  50 | });
```