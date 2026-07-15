import { test, expect } from '@playwright/test';

test.describe('TodoMVC-文章浏览与精读', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('未提供', { waitUntil: 'domcontentloaded' });
  });

  test('正常浏览文章列表并进入精读页', async ({ page }) => {
    await expect(page.getByTestId('article-list')).toBeVisible({ timeout: 10000 });
    await page.getByTestId('article-item').first().click();
    await expect(page.getByTestId('original-article-tab')).toBeVisible();
    await page.getByTestId('deconstruction-tab').click();
    await expect(page.getByTestId('deconstruction-content')).toBeVisible();
  });

  test('文章列表为空时显示提示信息', async ({ page }) => {
    await expect(page.getByText('暂无推送文章')).toBeVisible({ timeout: 5000 });
  });
});