# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-标记完成与删除 >> 清除所有已完成
- Location: testpilot-backend\generated\.runtime\3a5488c5\test.spec.ts:39:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.goto: net::ERR_TIMED_OUT at https://demo.playwright.dev/todomvc/
Call log:
  - navigating to "https://demo.playwright.dev/todomvc/", waiting until "domcontentloaded"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-标记完成与删除', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: net::ERR_TIMED_OUT at https://demo.playwright.dev/todomvc/
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
  35 |     await expect(page.getByRole('listitem')).toHaveCount(2);
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