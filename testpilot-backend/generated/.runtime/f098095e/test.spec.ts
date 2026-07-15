import { test, expect } from '@playwright/test';

test.describe('TodoMVC-任务异常输入测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/dashboard/tasks', { waitUntil: 'domcontentloaded' });
  });

  test('提交空的任务名应显示错误提示', async ({ page }) => {
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.getByText(/不能为空|必填|错误/)).toBeVisible();
  });

  test('提交超长的任务名应显示错误提示', async ({ page }) => {
    const longName = 'a'.repeat(1001);
    await page.getByPlaceholder('任务名称').fill(longName);
    await page.getByPlaceholder('描述').fill('描述');
    await page.getByPlaceholder('截止日期').fill('2025-12-31');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.getByText(/超出长度|太长|不能超过/)).toBeVisible();
  });
});