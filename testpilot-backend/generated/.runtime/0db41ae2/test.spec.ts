import { test, expect } from '@playwright/test';

test.describe('TodoMVC-任务添加功能测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/dashboard/tasks', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加任务', async ({ page }) => {
    await page.getByPlaceholder('任务名称').fill('测试任务');
    await page.getByPlaceholder('描述').fill('这是一个测试任务');
    await page.getByLabel('截止日期').fill('2025-12-31');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.getByText('测试任务')).toBeVisible();
  });

  test('添加任务名称为空', async ({ page }) => {
    await page.getByPlaceholder('描述').fill('测试描述');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.getByText('任务名称不能为空')).toBeVisible();
  });
});