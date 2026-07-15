import { test, expect } from '@playwright/test';

test.describe('每日推送 - 已删除文章点击', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
  const USERNAME = process.env.USERNAME || 'admin';
  const PASSWORD = process.env.PASSWORD || 'password';

  test.beforeEach(async ({ page }) => {
    // 模拟文章详情接口返回404
    await page.route('**/api/articles/**', async route => {
      await route.fulfill({ status: 404, body: JSON.stringify({ error: '文章不存在' }) });
    });
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await page.getByLabel('用户名').fill(USERNAME);
    await page.getByLabel('密码').fill(PASSWORD);
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  });

  test('验证点击已删除文章显示错误提示', async ({ page }) => {
    // 点击第一篇文章（假设后端将返回错误）
    await page.getByTestId('article-card').first().click();
    // 验证显示错误提示
    await expect(page.getByTestId('error-message')).toBeVisible();
    await expect(page.getByTestId('error-message')).toContainText('文章不存在');
  });
});