import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办', async ({ page }) => {
    const todoText = '学习Playwright';
    await page.getByPlaceholder('What needs to be done?').fill(todoText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.locator('ul.todo-list li').filter({ hasText: todoText })).toBeVisible();
    await expect(page.locator('.todo-count')).toHaveText('1 item left');
  });

  test('添加空文本不应创建待办', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('已有待办');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.locator('ul.todo-list li')).toHaveCount(1);

    await page.getByPlaceholder('What needs to be done?').fill('');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.locator('ul.todo-list li')).toHaveCount(1);

    await page.getByPlaceholder('What needs to be done?').fill('   ');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.locator('ul.todo-list li')).toHaveCount(1);
  });

  test('添加特殊字符待办', async ({ page }) => {
    const specialText = '<script>alert("xss")</script>';
    await page.getByPlaceholder('What needs to be done?').fill(specialText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.locator('ul.todo-list li').filter({ hasText: specialText })).toBeVisible();
  });
});