# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-过滤列表 >> 按状态过滤正常
- Location: testpilot-backend\generated\.runtime\aba90a63\test.spec.ts:10:7

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  getByRole('listitem')
Expected: 3
Received: 6
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" with timeout 5000ms
  - waiting for getByRole('listitem')
    14 × locator resolved to 6 elements
       - unexpected value "6"

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
            - generic [ref=e16]: 吃饭
            - text: ×
        - listitem [ref=e17]:
          - generic [ref=e18]:
            - checkbox "Toggle Todo" [checked] [ref=e19]
            - generic [ref=e20]: 睡觉
            - text: ×
        - listitem [ref=e21]:
          - generic [ref=e22]:
            - checkbox "Toggle Todo" [ref=e23]
            - generic [ref=e24]: 打豆豆
            - text: ×
    - generic [ref=e25]:
      - generic [ref=e26]:
        - strong [ref=e27]: "2"
        - text: items left
      - list [ref=e28]:
        - listitem [ref=e29]:
          - link "All" [active] [ref=e30] [cursor=pointer]:
            - /url: "#/"
        - listitem [ref=e31]:
          - link "Active" [ref=e32] [cursor=pointer]:
            - /url: "#/active"
        - listitem [ref=e33]:
          - link "Completed" [ref=e34] [cursor=pointer]:
            - /url: "#/completed"
      - button "Clear completed" [ref=e35] [cursor=pointer]
  - contentinfo [ref=e36]:
    - paragraph [ref=e37]: Double-click to edit a todo
    - paragraph [ref=e38]:
      - text: Created by
      - link "Remo H. Jansen" [ref=e39] [cursor=pointer]:
        - /url: http://github.com/remojansen/
    - paragraph [ref=e40]:
      - text: Part of
      - link "TodoMVC" [ref=e41] [cursor=pointer]:
        - /url: http://todomvc.com
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-过滤列表', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |     await page.evaluate(() => localStorage.clear());
  7  |     await page.reload({ waitUntil: 'domcontentloaded' });
  8  |   });
  9  | 
  10 |   test('按状态过滤正常', async ({ page }) => {
  11 |     const todos = ['吃饭', '睡觉', '打豆豆'];
  12 |     for (const text of todos) {
  13 |       await page.getByPlaceholder('What needs to be done?').fill(text);
  14 |       await page.getByPlaceholder('What needs to be done?').press('Enter');
  15 |     }
  16 |     await page.getByRole('listitem').filter({ hasText: '睡觉' }).getByRole('checkbox').check();
  17 |     await page.getByRole('link', { name: 'All' }).click();
> 18 |     await expect(page.getByRole('listitem')).toHaveCount(3);
     |                                              ^ Error: expect(locator).toHaveCount(expected) failed
  19 |     await page.getByRole('link', { name: 'Active' }).click();
  20 |     await expect(page.getByRole('listitem')).toHaveCount(2);
  21 |     await expect(page.getByText('吃饭')).toBeVisible();
  22 |     await expect(page.getByText('打豆豆')).toBeVisible();
  23 |     await expect(page.getByText('睡觉')).not.toBeVisible();
  24 |     await page.getByRole('link', { name: 'Completed' }).click();
  25 |     await expect(page.getByRole('listitem')).toHaveCount(1);
  26 |     await expect(page.getByText('睡觉')).toBeVisible();
  27 |     await expect(page.getByText('吃饭')).not.toBeVisible();
  28 |     await expect(page.getByText('打豆豆')).not.toBeVisible();
  29 |   });
  30 | 
  31 |   test('空列表下过滤', async ({ page }) => {
  32 |     await expect(page.getByRole('listitem')).toHaveCount(0);
  33 |     await page.getByRole('link', { name: 'Active' }).click();
  34 |     await expect(page.getByRole('listitem')).toHaveCount(0);
  35 |     await page.getByRole('link', { name: 'Completed' }).click();
  36 |     await expect(page.getByRole('listitem')).toHaveCount(0);
  37 |     await page.getByRole('link', { name: 'All' }).click();
  38 |     await expect(page.getByRole('listitem')).toHaveCount(0);
  39 |     await expect(page.getByText(/items? left/)).not.toBeVisible();
  40 |   });
  41 | });
```