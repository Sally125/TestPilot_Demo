import { test, expect } from '@playwright/test';

test.describe('每日推送 - 文章排序', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
  const USERNAME = process.env.USERNAME || 'admin';
  const PASSWORD = process.env.PASSWORD || 'password';

  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await page.getByLabel('用户名').fill(USERNAME);
    await page.getByLabel('密码').fill(PASSWORD);
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  });

  test('验证文章列表按推送时间倒序排列', async ({ page }) => {
    const articleList = page.getByTestId('article-list');
    await expect(articleList).toBeVisible();
    // 获取前两篇文章的发布时间
    const firstTime = await articleList.getByTestId('article-card').first().getByTestId('article-time').textContent();
    const secondTime = await articleList.getByTestId('article-card').nth(1).getByTestId('article-time').textContent();
    // 比较时间（假设时间字符串可直接比较，如'2025-03-10 10:00'）
    expect(new Date(firstTime).getTime()).toBeGreaterThan(new Date(secondTime).getTime());
  });
});