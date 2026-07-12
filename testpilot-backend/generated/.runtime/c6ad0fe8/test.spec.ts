import { test, expect } from '@playwright/test';

test.describe('TodoMVC-BasicOps', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('add todo item', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('TestItem');
    await page.keyboard.press('Enter');
    await expect(page.getByText('TestItem')).toBeVisible();
    await expect(page.locator('.todo-list li')).toHaveCount(1);
  });

  test('empty input should not add', async ({ page }) => {
    const initialCount = await page.locator('.todo-list li').count();
    await page.getByPlaceholder('What needs to be done?').fill('');
    await page.keyboard.press('Enter');
    await expect(page.locator('.todo-list li')).toHaveCount(initialCount);
  });
});