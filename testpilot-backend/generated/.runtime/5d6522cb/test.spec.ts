import { test, expect } from '@playwright/test';
test.describe('TodoMVC-添加待办事项', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });
  test('正常添加待办事项', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('测试待办');
    await input.press('Enter');
    await expect(page.getByText('测试待办')).toBeVisible();
    await expect(page.getByText(/1 item left/)).toBeVisible();
  });
  test('添加空输入不应新增待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('');
    await input.press('Enter');
    await expect(page.getByRole('listitem')).toHaveCount(0);
    await expect(page.getByText('0 items left')).toBeVisible();
  });
  test('添加纯空格输入不应新增待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('   ');
    await input.press('Enter');
    await expect(page.getByRole('listitem')).toHaveCount(0);
    await expect(page.getByText('0 items left')).toBeVisible();
  });
});