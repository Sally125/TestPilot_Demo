import { test, expect } from '@playwright/test';

test.describe('TodoMVC-标记待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('标记完成', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('测试待办');
    await input.press('Enter');
    const checkbox = page.locator('li').filter({ hasText: '测试待办' }).getByRole('checkbox');
    await checkbox.click();
    await expect(checkbox).toBeChecked();
    await expect(page.getByText('0 items left')).toBeVisible();
  });

  test('取消完成', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('测试待办');
    await input.press('Enter');
    const checkbox = page.locator('li').filter({ hasText: '测试待办' }).getByRole('checkbox');
    await checkbox.click();
    await expect(checkbox).toBeChecked();
    await checkbox.click();
    await expect(checkbox).not.toBeChecked();
    await expect(page.getByText('1 item left')).toBeVisible();
  });
});