import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办事项', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办事项', async ({ page }) => {
    const task = '测试任务1';
    await page.getByPlaceholder('What needs to be done?').fill(task);
    await page.keyboard.press('Enter');
    await expect(page.getByText(task)).toBeVisible();
  });

  test('不允许添加空待办事项', async ({ page }) => {
    const initialCount = await page.getByRole('listitem').count();
    await page.getByPlaceholder('What needs to be done?').fill('');
    await page.keyboard.press('Enter');
    await expect(page.getByRole('listitem')).toHaveCount(initialCount);
  });

  test('添加超长文本待办事项', async ({ page }) => {
    const longTask = '这是一段超长的待办事项文本，用于测试边界值输入，长度可能超过显示区域，但应该允许添加。';
    await page.getByPlaceholder('What needs to be done?').fill(longTask);
    await page.keyboard.press('Enter');
    await expect(page.getByText(longTask)).toBeVisible();
  });
});