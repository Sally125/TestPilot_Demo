import { test, expect } from '@playwright/test';

test.describe('TodoMVC-标记完成', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('测试待办');
    await input.press('Enter');
  });

  test('标记待办为完成', async ({ page }) => {
    const todoItem = page.locator('.todo-list li').filter({ hasText: '测试待办' });
    await todoItem.getByRole('checkbox').click();
    await expect(todoItem).toHaveClass('completed');
    await expect(todoItem.getByRole('checkbox')).toBeChecked();
    await expect(page.getByText('0 items left')).toBeVisible();
  });

  test('取消标记完成', async ({ page }) => {
    const todoItem = page.locator('.todo-list li').filter({ hasText: '测试待办' });
    const checkbox = todoItem.getByRole('checkbox');
    await checkbox.click();
    await expect(todoItem).toHaveClass('completed');
    await checkbox.click();
    await expect(todoItem).not.toHaveClass('completed');
    await expect(checkbox).not.toBeChecked();
    await expect(page.getByText('1 item left')).toBeVisible();
  });
});