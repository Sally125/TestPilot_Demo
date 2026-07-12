import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办-正常流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('添加一个待办项', async ({ page }) => {
    const todoText = '测试待办1';
    await page.getByPlaceholder('What needs to be done?').fill(todoText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(todoText)).toBeVisible();
    // 验证计数显示为1
    await expect(page.getByText('1 item left')).toBeVisible();
  });

  test('添加多个待办项', async ({ page }) => {
    const todos = ['待办A', '待办B'];
    for (const text of todos) {
      await page.getByPlaceholder('What needs to be done?').fill(text);
      await page.getByPlaceholder('What needs to be done?').press('Enter');
    }
    await expect(page.getByText('待办A')).toBeVisible();
    await expect(page.getByText('待办B')).toBeVisible();
    await expect(page.getByText('2 items left')).toBeVisible();
  });
});