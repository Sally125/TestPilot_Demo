import { test, expect } from '@playwright/test';

test.describe('TodoMVC-标记完成与删除', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('待办一');
    await input.press('Enter');
    await input.fill('待办二');
    await input.press('Enter');
    await input.fill('待办三');
    await input.press('Enter');
  });

  test('标记完成并取消完成', async ({ page }) => {
    await page.getByLabel('待办二').check();
    await expect(page.getByText('待办二')).toHaveClass(/completed/);
    await page.getByLabel('待办二').uncheck();
    await expect(page.getByText('待办二')).not.toHaveClass(/completed/);
  });

  test('删除待办项', async ({ page }) => {
    const todoItem = page.locator('li', { hasText: '待办一' });
    await todoItem.hover();
    await todoItem.locator('button.destroy').click();
    await expect(page.getByText('待办一')).toHaveCount(0);
    await expect(page.locator('.todo-count')).toHaveText('2 items left');
  });

  test('清除已完成的待办', async ({ page }) => {
    await page.getByLabel('待办一').check();
    await page.getByLabel('待办二').check();
    await page.getByText('Clear completed').click();
    await expect(page.locator('.todo-list li')).toHaveCount(1);
    await expect(page.getByText('待办三')).toBeVisible();
    await expect(page.locator('.todo-count')).toHaveText('1 item left');
  });
});