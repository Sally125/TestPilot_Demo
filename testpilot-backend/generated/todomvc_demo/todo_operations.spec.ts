import { test, expect } from '@playwright/test';

test.describe('TodoMVC-待办操作', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('添加新待办事项', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Buy milk');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText('Buy milk')).toBeVisible();
  });

  test('完成待办事项', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Learn Playwright');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByRole('checkbox', { name: 'Toggle Todo' }).check();
    await expect(page.locator('.todo-list li.completed')).toHaveCount(1);
  });

  test('删除待办事项', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Delete me');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    const item = page.getByText('Delete me');
    await item.hover();
    await page.locator('.destroy').click();
    await expect(item).not.toBeVisible();
  });
});