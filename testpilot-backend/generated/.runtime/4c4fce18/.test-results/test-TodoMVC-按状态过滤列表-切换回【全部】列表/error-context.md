# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-按状态过滤列表 >> 切换回【全部】列表
- Location: testpilot-backend\generated\.runtime\4c4fce18\test.spec.ts:31:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: locator.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByPlaceholder('What needs to be done?')

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
  3  | test.describe('TodoMVC-按状态过滤列表', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
> 6  |     await page.getByPlaceholder('What needs to be done?').fill('待办1');
     |                                                           ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  7  |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  8  |     await page.getByPlaceholder('What needs to be done?').fill('待办2');
  9  |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  10 |     await page.getByPlaceholder('What needs to be done?').fill('待办3');
  11 |     await page.getByPlaceholder('What needs to be done?').press('Enter');
  12 |     await page.locator('li').filter({ hasText: '待办2' }).locator('input[type="checkbox"]').click();
  13 |   });
  14 | 
  15 |   test('过滤【待办】列表', async ({ page }) => {
  16 |     await page.getByRole('link', { name: 'Active' }).click();
  17 |     await expect(page.locator('ul.todo-list li')).toHaveCount(2);
  18 |     await expect(page.locator('li').filter({ hasText: '待办1' })).toBeVisible();
  19 |     await expect(page.locator('li').filter({ hasText: '待办3' })).toBeVisible();
  20 |     await expect(page.locator('li').filter({ hasText: '待办2' })).not.toBeVisible();
  21 |     await expect(page.locator('.todo-count')).toHaveText('2 items left');
  22 |   });
  23 | 
  24 |   test('过滤【已完成】列表', async ({ page }) => {
  25 |     await page.getByRole('link', { name: 'Completed' }).click();
  26 |     await expect(page.locator('ul.todo-list li')).toHaveCount(1);
  27 |     await expect(page.locator('li').filter({ hasText: '待办2' })).toBeVisible();
  28 |     await expect(page.locator('li').filter({ hasText: '待办1' })).not.toBeVisible();
  29 |   });
  30 | 
  31 |   test('切换回【全部】列表', async ({ page }) => {
  32 |     await page.getByRole('link', { name: 'Active' }).click();
  33 |     await expect(page.locator('ul.todo-list li')).toHaveCount(2);
  34 |     await page.getByRole('link', { name: 'All' }).click();
  35 |     await expect(page.locator('ul.todo-list li')).toHaveCount(3);
  36 |   });
  37 | });
```