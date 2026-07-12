# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-添加待办 >> 空输入不添加
- Location: testpilot-backend\generated\.runtime\cc18efa6\test.spec.ts:16:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
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
  3  | test.describe('TodoMVC-添加待办', () => {
> 4  |   test.beforeEach(async ({ page }) => {
     |        ^ Test timeout of 30000ms exceeded while running "beforeEach" hook.
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  6  |   });
  7  | 
  8  |   test('正常添加待办', async ({ page }) => {
  9  |     const input = page.getByPlaceholder('What needs to be done?');
  10 |     await input.fill('Buy milk');
  11 |     await page.keyboard.press('Enter');
  12 |     await expect(page.getByText('Buy milk')).toBeVisible();
  13 |     await expect(page.getByText('1 item left')).toBeVisible();
  14 |   });
  15 | 
  16 |   test('空输入不添加', async ({ page }) => {
  17 |     const input = page.getByPlaceholder('What needs to be done?');
  18 |     await input.fill('   ');
  19 |     await page.keyboard.press('Enter');
  20 |     await expect(page.getByRole('listitem')).toHaveCount(0);
  21 |   });
  22 | 
  23 |   test('添加特殊字符不被转义', async ({ page }) => {
  24 |     const special = '<b>HTML</b>';
  25 |     await page.getByPlaceholder('What needs to be done?').fill(special);
  26 |     await page.keyboard.press('Enter');
  27 |     await expect(page.getByRole('listitem').filter({ hasText: special })).toHaveCount(1);
  28 |     await expect(page.getByRole('listitem').filter({ hasText: special })).toContainText(special);
  29 |   });
  30 | });
```