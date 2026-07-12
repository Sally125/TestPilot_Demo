import { test, expect } from '@playwright/test';

test.describe('TodoMVC-按状态过滤列表', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('任务一');
    await input.press('Enter');
    await input.fill('任务二');
    await input.press('Enter');
    await input.fill('任务三');
    await input.press('Enter');
    await page.getByLabel('任务一').check();
  });

  test('按状态筛选列表', async ({ page }) => {
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.locator('.todo-list li')).toHaveCount(2);
    await expect(page.getByText('任务二')).toBeVisible();
    await expect(page.getByText('任务三')).toBeVisible();
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.locator('.todo-list li')).toHaveCount(1);
    await expect(page.getByText('任务一')).toBeVisible();
    await page.getByRole('link', { name: 'All' }).click();
    await expect(page.locator('.todo-list li')).toHaveCount(3);
  });

  test('在过滤状态下进行操作', async ({ page }) => {
    await page.getByRole('link', { name: 'Active' }).click();
    await page.getByLabel('任务二').check();
    await expect(page.locator('.todo-list li')).toHaveCount(1);
    await expect(page.getByText('任务三')).toBeVisible();
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.locator('.todo-list li')).toHaveCount(2);
    const completedItem = page.locator('li', { hasText: '任务一' });
    await completedItem.hover();
    await completedItem.locator('button.destroy').click();
    await expect(page.locator('.todo-list li')).toHaveCount(1);
    await page.getByRole('link', { name: 'All' }).click();
    await expect(page.locator('.todo-list li')).toHaveCount(2);
  });
});