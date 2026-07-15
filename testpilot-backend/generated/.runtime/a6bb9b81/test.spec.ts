import { test, expect } from '@playwright/test';

test.describe('每日推送文章列表', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/dashboard', { waitUntil: 'domcontentloaded' });
  });

  test('环境验证: 页面加载成功', async ({ page }) => {
    await expect(page.getByTestId('page-container')).toBeVisible();
  });

  test('TC-001: 文章列表正常加载并展示基本信息', async ({ page }) => {
    await expect(page.getByTestId('article-list')).toBeVisible();
    const cards = page.getByTestId('article-card');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(10);
    const firstCard = cards.first();
    await expect(firstCard.getByTestId('article-title')).toBeVisible();
    await expect(firstCard.getByTestId('article-summary')).toBeVisible();
    await expect(firstCard.getByTestId('article-publish-time')).toBeVisible();
  });
});