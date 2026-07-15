import { test, expect } from '@playwright/test';

test.describe('TodoMVC-删除待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('删除一个待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('待办A');
    await input.press('Enter');
    const todoItem = page.locator('li').filter({ hasText: '待办A' });
    await todoItem.hover();
    await todoItem.getByText('×').click();
    await expect(todoItem).not.toBeVisible();
    await expect(page.getByText('0 items left')).toBeVisible();
  });

  test('删除一个后剩余待办计数正确', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('待办A');
    await input.press('Enter');
    await input.fill('待办B');
    await input.press('Enter');
    const todoA = page.locator('li').filter({ hasText: '待办A' });
    await todoA.hover();
    await todoA.getByText('×').click();
    await expect(todoA).not.toBeVisible();
    await expect(page.getByText('待办B')).toBeVisible();
    await expect(page.getByText('1 item left')).toBeVisible();
  });
});