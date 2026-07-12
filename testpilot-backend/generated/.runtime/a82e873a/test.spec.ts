import { test, expect } from '@playwright/test';

test.describe('TodoMVC-标记完成与删除', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    await page.getByPlaceholder('What needs to be done?').fill('待办A');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByPlaceholder('What needs to be done?').fill('待办B');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.locator('ul.todo-list li')).toHaveCount(2);
  });

  test('标记完成与取消完成', async ({ page }) => {
    const todoA = page.locator('li').filter({ hasText: '待办A' });
    const checkbox = todoA.locator('input[type="checkbox"]');
    await checkbox.click();
    await expect(checkbox).toBeChecked();
    await expect(page.locator('.todo-count')).toHaveText('1 item left');
    await checkbox.click();
    await expect(checkbox).not.toBeChecked();
    await expect(page.locator('.todo-count')).toHaveText('2 items left');
  });

  test('删除单条待办', async ({ page }) => {
    const todoB = page.locator('li').filter({ hasText: '待办B' });
    await todoB.hover();
    const deleteButton = todoB.locator('button.destroy');
    await deleteButton.click();
    await expect(todoB).not.toBeVisible();
    await expect(page.locator('ul.todo-list li')).toHaveCount(1);
    await expect(page.locator('.todo-count')).toHaveText('1 item left');
  });

  test('清除已完成待办', async ({ page }) => {
    const todoA = page.locator('li').filter({ hasText: '待办A' });
    await todoA.locator('input[type="checkbox"]').click();
    const todoB = page.locator('li').filter({ hasText: '待办B' });
    await todoB.locator('input[type="checkbox"]').click();
    await page.getByRole('button', { name: 'Clear completed' }).click();
    await expect(page.locator('ul.todo-list li')).toHaveCount(0);
    await expect(page.locator('.todo-count')).toHaveText('0 items left');
  });
});