import { test, expect } from '@playwright/test';

test.describe('TodoMVC-过滤列表', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'domcontentloaded' });
  });

  test('按状态过滤正常', async ({ page }) => {
    const todos = ['吃饭', '睡觉', '打豆豆'];
    for (const text of todos) {
      await page.getByPlaceholder('What needs to be done?').fill(text);
      await page.getByPlaceholder('What needs to be done?').press('Enter');
    }
    await page.getByRole('listitem').filter({ hasText: '睡觉' }).getByRole('checkbox').check();
    await page.getByRole('link', { name: 'All' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(3);
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(2);
    await expect(page.getByText('吃饭')).toBeVisible();
    await expect(page.getByText('打豆豆')).toBeVisible();
    await expect(page.getByText('睡觉')).not.toBeVisible();
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(1);
    await expect(page.getByText('睡觉')).toBeVisible();
    await expect(page.getByText('吃饭')).not.toBeVisible();
    await expect(page.getByText('打豆豆')).not.toBeVisible();
  });

  test('空列表下过滤', async ({ page }) => {
    await expect(page.getByRole('listitem')).toHaveCount(0);
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(0);
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(0);
    await page.getByRole('link', { name: 'All' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(0);
    await expect(page.getByText(/items? left/)).not.toBeVisible();
  });
});