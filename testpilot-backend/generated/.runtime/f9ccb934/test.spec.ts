import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    // 清除本地存储确保测试独立
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办', async ({ page }) => {
    const todoText = '学习Playwright';
    await page.getByPlaceholder('What needs to be done?').fill(todoText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(todoText)).toBeVisible();
  });

  test('添加超长文本待办', async ({ page }) => {
    const longText = 'A'.repeat(1000);
    await page.getByPlaceholder('What needs to be done?').fill(longText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(longText)).toBeVisible();
  });

  test('添加空文本不创建待办', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByRole('listitem')).toHaveCount(0);
  });

  test('添加仅空格文本不创建待办', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('   ');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByRole('listitem')).toHaveCount(0);
  });
});