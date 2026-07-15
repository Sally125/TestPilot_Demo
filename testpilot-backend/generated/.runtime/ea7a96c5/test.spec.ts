import { test, expect } from '@playwright/test';

test.describe('TodoMVC-删除待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('待办1');
    await input.press('Enter');
    await input.fill('待办2');
    await input.press('Enter');
  });

  test('删除待办项', async ({ page }) => {
    const todoItem = page.locator('.todo-list li').filter({ hasText: '待办1' });
    await todoItem.hover();
    await todoItem.locator('button.destroy').click();
    await expect(todoItem).not.toBeVisible();
    await expect(page.locator('.todo-list li')).toHaveCount(1);
    await expect(page.getByText('1 item left')).toBeVisible();
  });

  test('删除已完成待办', async ({ page }) => {
    const todoItem1 = page.locator('.todo-list li').filter({ hasText: '待办1' });
    await todoItem1.getByRole('checkbox').click();
    await todoItem1.hover();
    await todoItem1.locator('button.destroy').click();
    await expect(page.locator('.todo-list li')).toHaveCount(1);
    await expect(page.getByText('1 item left')).toBeVisible();
  });

  test('删除最后一个待办显示空状态', async ({ page }) => {
    const items = page.locator('.todo-list li');
    let count = await items.count();
    for (let i = 0; i < count; i++) {
      const item = items.nth(0);
      await item.hover();
      await item.locator('button.destroy').click();
    }
    await expect(page.locator('.todo-list li')).toHaveCount(0);
  });
});