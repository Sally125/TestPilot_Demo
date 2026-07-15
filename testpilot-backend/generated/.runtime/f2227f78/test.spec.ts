import { test, expect } from '@playwright/test';

test.describe('TodoMVC-任务边界值测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/dashboard/tasks', { waitUntil: 'domcontentloaded' });
  });

  test('任务名称为最小长度（1个字符）应能创建成功', async ({ page }) => {
    await page.getByPlaceholder('任务名称').fill('a');
    await page.getByPlaceholder('描述').fill('描述');
    await page.getByPlaceholder('截止日期').fill('2025-12-31');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.getByText('a')).toBeVisible();
  });

  test('任务名称为最大长度（1000个字符）应能创建成功', async ({ page }) => {
    const name = 'a'.repeat(1000);
    await page.getByPlaceholder('任务名称').fill(name);
    await page.getByPlaceholder('描述').fill('描述');
    await page.getByPlaceholder('截止日期').fill('2025-12-31');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.getByText(name)).toBeVisible();
  });
});