import { test, expect } from '@playwright/test';

test.describe('每日推送 - 文章列表加载与展示', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3001/dashboard';
  const USERNAME = process.env.USERNAME || 'admin';
  const PASSWORD = process.env.PASSWORD || 'password';

  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await page.getByLabel('用户名').fill(USERNAME);
    await page.getByLabel('密码').fill(PASSWORD);
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  });

  test('验证文章列表正常加载并显示标题、摘要和发布时间', async ({ page }) => {
    // 等待文章列表区域可见
    const articleList = page.getByTestId('article-list');
    await expect(articleList).toBeVisible();
    // 检查第一篇文章包含标题、摘要、发布时间
    const firstArticle = articleList.getByTestId('article-card').first();
    await expect(firstArticle).toBeVisible();
    await expect(firstArticle.getByTestId('article-title')).toBeVisible();
    await expect(firstArticle.getByTestId('article-summary')).toBeVisible();
    await expect(firstArticle.getByTestId('article-time')).toBeVisible();
    // 验证时间格式（简单检查日期模式）
    const timeText = await firstArticle.getByTestId('article-time').textContent();
    expect(timeText).toMatch(/\d{4}-\d{2}-\d{2}/);
  });
});