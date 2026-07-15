import { test, expect } from '@playwright/test';

test.describe('每日推送 - 加载状态', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
  const USERNAME = process.env.USERNAME || 'admin';
  const PASSWORD = process.env.PASSWORD || 'password';

  test.beforeEach(async ({ page }) => {
    // 模拟文章接口延迟，确保加载指示器可见
    await page.route('**/api/articles**', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000)); // 延迟2秒
      await route.continue();
    });
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await page.getByLabel('用户名').fill(USERNAME);
    await page.getByLabel('密码').fill(PASSWORD);
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  });

  test('验证文章列表加载时显示加载状态', async ({ page }) => {
    // 检查加载指示器出现
    const loadingIndicator = page.getByTestId('loading-indicator');
    await expect(loadingIndicator).toBeVisible();
    // 等待加载完成，指示器消失
    await expect(loadingIndicator).not.toBeVisible({ timeout: 10000 });
    // 文章列表可见
    await expect(page.getByTestId('article-list')).toBeVisible();
  });
});