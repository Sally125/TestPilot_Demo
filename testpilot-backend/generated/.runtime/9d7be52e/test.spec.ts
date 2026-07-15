import { test, expect } from '@playwright/test';

test.describe('每日推送 - 文章点击跳转', () => {
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

  test('验证点击文章卡片跳转至正确详情页', async ({ page }) => {
    // 获取第一篇文章的标题用于验证
    const firstArticleTitle = await page.getByTestId('article-card').first().getByTestId('article-title').textContent();
    // 点击文章卡片
    await page.getByTestId('article-card').first().click();
    // 等待页面跳转到详情页，URL包含文章ID或标题
    await expect(page).toHaveURL(/\/articles\//);
    // 检查详情页标题与列表一致
    await expect(page.getByTestId('article-detail-title')).toHaveText(firstArticleTitle);
  });
});