# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-标记待办 >> 取消完成
- Location: testpilot-backend\generated\.runtime\c08a241c\test.spec.ts:18:7

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
  3  | test.describe('TodoMVC-标记待办', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: Test timeout of 30000ms exceeded.
  6  |   });
  7  | 
  8  |   test('标记完成', async ({ page }) => {
  9  |     const input = page.getByPlaceholder('What needs to be done?');
  10 |     await input.fill('测试待办');
  11 |     await input.press('Enter');
  12 |     const checkbox = page.locator('li').filter({ hasText: '测试待办' }).getByRole('checkbox');
  13 |     await checkbox.click();
  14 |     await expect(checkbox).toBeChecked();
  15 |     await expect(page.getByText('0 items left')).toBeVisible();
  16 |   });
  17 | 
  18 |   test('取消完成', async ({ page }) => {
  19 |     const input = page.getByPlaceholder('What needs to be done?');
  20 |     await input.fill('测试待办');
  21 |     await input.press('Enter');
  22 |     const checkbox = page.locator('li').filter({ hasText: '测试待办' }).getByRole('checkbox');
  23 |     await checkbox.click();
  24 |     await expect(checkbox).toBeChecked();
  25 |     await checkbox.click();
  26 |     await expect(checkbox).not.toBeChecked();
  27 |     await expect(page.getByText('1 item left')).toBeVisible();
  28 |   });
  29 | });
```