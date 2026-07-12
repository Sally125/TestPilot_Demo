import { test, expect } from '@playwright/test';
test.describe('TodoMVC-删除待办事项', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('待办一');
    await input.press('Enter');
    await input.fill('待办二');
    await input.press('Enter');
  });
  test('删除一个待办项', async ({ page }) => {
    const todoItem = page.getByRole('listitem').filter({ hasText: '待办一' });
    await todoItem.hover();
    await todoItem.locator('button').click();
    await expect(page.getByText('待办一')).not.toBeVisible();
    await expect(page.getByText('1 item left')).toBeVisible();
  });
  test('删除所有待办项', async ({ page }) => {
    const item1 = page.getByRole('listitem').filter({ hasText: '待办一' });
    await item1.hover();
    await item1.locator('button').click();
    const item2 = page.getByRole('listitem').filter({ hasText: '待办二' });
    await item2.hover();
    await item2.locator('button').click();
    await expect(page.getByRole('listitem')).toHaveCount(0);
    await expect(page.getByText('0 items left')).toBeVisible();
  });
});