import { test, expect } from '@playwright/test';

test.describe('TodoMVC - 标记完成与删除', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('标记完成和取消完成', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('任务A');
    await input.press('Enter');
    await input.fill('任务B');
    await input.press('Enter');

    const taskA = page.getByRole('listitem').filter({ hasText: '任务A' });
    const checkbox = taskA.getByRole('checkbox');
    await checkbox.check();
    await expect(checkbox).toBeChecked();
    await expect(taskA).toHaveClass(/completed/);
    await checkbox.uncheck();
    await expect(checkbox).not.toBeChecked();
    await expect(taskA).not.toHaveClass(/completed/);
  });

  test('删除单个待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('待删除');
    await input.press('Enter');

    const item = page.getByRole('listitem').filter({ hasText: '待删除' });
    await item.hover();
    await item.getByRole('button').click();
    await expect(item).not.toBeVisible();
  });

  test('清除已完成待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('完成项');
    await input.press('Enter');
    await input.fill('未完成项');
    await input.press('Enter');

    const completedItem = page.getByRole('listitem').filter({ hasText: '完成项' });
    await completedItem.getByRole('checkbox').check();

    const clearButton = page.getByRole('button', { name: 'Clear completed' });
    await clearButton.click();

    await expect(page.getByText('完成项')).not.toBeVisible();
    await expect(page.getByText('未完成项')).toBeVisible();
  });
});