import { test, expect } from '@playwright/test';

test.describe('TodoMVC-页面元素验证', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('页面标题包含TodoMVC', async ({ page }) => {
    await expect(page).toHaveTitle(/TodoMVC/);
  });

  test('输入框存在且placeholder正确', async ({ page }) => {
    await expect(page.getByPlaceholder('What needs to be done?')).toBeVisible();
  });

  test('页脚链接显示正确', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Test');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByRole('link', { name: 'All' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Active' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Completed' })).toBeVisible();
  });
});