import { test, expect } from '@playwright/test';

test.describe('TodoMVC-任务边界值测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/dashboard/tasks', { waitUntil: 'domcontentloaded' });
  });

  test('超长任务名称', async ({ page }) => {
    const longName = 'a'.repeat(51);
    await page.getByPlaceholder('任务名称').fill(longName);
    await page.getByPlaceholder('描述').fill('边界测试');
    await page.getByRole('button', { name: '提交' }).click();
    // 预期：要么成功创建（名称可能被截断或完整显示），要么提示错误
    await expect(page.getByText(longName).or(page.getByText('名称过长'))).toBeVisible();
  });

  test('特殊字符任务名称', async ({ page }) => {
    const specialName = '<script>alert("xss")</script>';
    await page.getByPlaceholder('任务名称').fill(specialName);
    await page.getByRole('button', { name: '提交' }).click();
    // 验证：任务创建或显示经过转义的内容
    await expect(page.getByText('script')).toBeVisible();
  });
});