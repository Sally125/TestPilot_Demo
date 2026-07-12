import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加任务-边界与多项', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('添加任务-输入长度边界', async ({ page }) => {
    const longText = 'a'.repeat(1000);
    await page.getByPlaceholder('What needs to be done?').fill(longText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(longText).first()).toBeVisible();
  });

  test('添加多项任务并验证计数', async ({ page }) => {
    const tasks = ['任务一', '任务二', '任务三'];
    for (const task of tasks) {
      await page.getByPlaceholder('What needs to be done?').fill(task);
      await page.getByPlaceholder('What needs to be done?').press('Enter');
    }
    await expect(page.locator('.todo-list li')).toHaveCount(3);
    await expect(page.getByText('3 items left')).toBeVisible();
  });
});