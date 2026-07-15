import { test, expect } from '@playwright/test';

test.describe('TodoMVC-任务创建功能测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/dashboard/tasks', { waitUntil: 'domcontentloaded' });
  });

  test('正常情况下可以成功创建任务', async ({ page }) => {
    await page.getByPlaceholder('任务名称').fill('测试任务');
    await page.getByPlaceholder('描述').fill('这是描述');
    await page.getByPlaceholder('截止日期').fill('2025-12-31');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.getByText('测试任务')).toBeVisible();
  });

  test('创建任务后任务列表显示正确信息', async ({ page }) => {
    await page.getByPlaceholder('任务名称').fill('第二个任务');
    await page.getByPlaceholder('描述').fill('描述2');
    await page.getByPlaceholder('截止日期').fill('2025-12-30');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.getByText('第二个任务')).toBeVisible();
    await expect(page.getByText('描述2')).toBeVisible();
    await expect(page.getByText('2025-12-30')).toBeVisible();
  });
});