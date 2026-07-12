import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办-基本流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('输入有效内容添加待办', async ({ page }) => {
    const todoText = '购买水果';
    await page.getByPlaceholder('What needs to be done?').fill(todoText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(todoText)).toBeVisible();
  });

  test('输入空字符串不添加待办', async ({ page }) => {
    const initialCount = await page.getByRole('listitem').count();
    await page.getByPlaceholder('What needs to be done?').fill('');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByRole('listitem')).toHaveCount(initialCount);
  });
});