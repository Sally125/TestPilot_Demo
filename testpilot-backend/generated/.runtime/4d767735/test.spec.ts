import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办-异常流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('空输入不添加待办', async ({ page }) => {
    // 先添加一个待办作为参照
    await page.getByPlaceholder('What needs to be done?').fill('预设待办');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText('1 item left')).toBeVisible();

    // 空输入并回车
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    // 等待确认没有新待办
    await expect(page.getByText('1 item left')).toBeVisible();
    // 同时确保列表项数量仍为1
    await expect(page.locator('.todo-list li')).toHaveCount(1);
  });

  test('空格输入不添加待办', async ({ page }) => {
    // 先添加一个待办作为基数
    await page.getByPlaceholder('What needs to be done?').fill('已有待办');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText('1 item left')).toBeVisible();

    // 输入空格并回车
    await page.getByPlaceholder('What needs to be done?').fill('   ');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    // 列表项数量应不变
    await expect(page.locator('.todo-list li')).toHaveCount(1);
    // 左下角计数仍为1
    await expect(page.getByText('1 item left')).toBeVisible();
  });
});