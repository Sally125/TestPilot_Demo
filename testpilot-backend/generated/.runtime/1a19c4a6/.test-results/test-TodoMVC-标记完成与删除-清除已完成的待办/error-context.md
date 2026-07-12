# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-标记完成与删除 >> 清除已完成的待办
- Location: testpilot-backend\generated\.runtime\1a19c4a6\test.spec.ts:30:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.check: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByLabel('待办一')

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
            - generic [ref=e16]: 待办一
            - text: ×
        - listitem [ref=e17]:
          - generic [ref=e18]:
            - checkbox "Toggle Todo" [ref=e19]
            - generic [ref=e20]: 待办二
            - text: ×
        - listitem [ref=e21]:
          - generic [ref=e22]:
            - checkbox "Toggle Todo" [ref=e23]
            - generic [ref=e24]: 待办三
            - text: ×
    - generic [ref=e25]:
      - generic [ref=e26]:
        - strong [ref=e27]: "3"
        - text: items left
      - list [ref=e28]:
        - listitem [ref=e29]:
          - link "All" [ref=e30] [cursor=pointer]:
            - /url: "#/"
        - listitem [ref=e31]:
          - link "Active" [ref=e32] [cursor=pointer]:
            - /url: "#/active"
        - listitem [ref=e33]:
          - link "Completed" [ref=e34] [cursor=pointer]:
            - /url: "#/completed"
  - contentinfo [ref=e35]:
    - paragraph [ref=e36]: Double-click to edit a todo
    - paragraph [ref=e37]:
      - text: Created by
      - link "Remo H. Jansen" [ref=e38] [cursor=pointer]:
        - /url: http://github.com/remojansen/
    - paragraph [ref=e39]:
      - text: Part of
      - link "TodoMVC" [ref=e40] [cursor=pointer]:
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
  7  |     await input.fill('待办一');
  8  |     await input.press('Enter');
  9  |     await input.fill('待办二');
  10 |     await input.press('Enter');
  11 |     await input.fill('待办三');
  12 |     await input.press('Enter');
  13 |   });
  14 | 
  15 |   test('标记完成并取消完成', async ({ page }) => {
  16 |     await page.getByLabel('待办二').check();
  17 |     await expect(page.getByText('待办二')).toHaveClass(/completed/);
  18 |     await page.getByLabel('待办二').uncheck();
  19 |     await expect(page.getByText('待办二')).not.toHaveClass(/completed/);
  20 |   });
  21 | 
  22 |   test('删除待办项', async ({ page }) => {
  23 |     const todoItem = page.locator('li', { hasText: '待办一' });
  24 |     await todoItem.hover();
  25 |     await todoItem.locator('button.destroy').click();
  26 |     await expect(page.getByText('待办一')).toHaveCount(0);
  27 |     await expect(page.locator('.todo-count')).toHaveText('2 items left');
  28 |   });
  29 | 
  30 |   test('清除已完成的待办', async ({ page }) => {
> 31 |     await page.getByLabel('待办一').check();
     |                                  ^ Error: locator.check: Test timeout of 30000ms exceeded.
  32 |     await page.getByLabel('待办二').check();
  33 |     await page.getByText('Clear completed').click();
  34 |     await expect(page.locator('.todo-list li')).toHaveCount(1);
  35 |     await expect(page.getByText('待办三')).toBeVisible();
  36 |     await expect(page.locator('.todo-count')).toHaveText('1 item left');
  37 |   });
  38 | });
```