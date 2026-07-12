import { test, expect } from '@playwright/test';

test('截图编码测试-添加待办', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/');
  await page.getByPlaceholder('What needs to be done?').fill('测试待办项');
  await page.getByPlaceholder('What needs to be done?').press('Enter');
  await expect(page.getByTestId('todo-item')).toHaveCount(1);
});
