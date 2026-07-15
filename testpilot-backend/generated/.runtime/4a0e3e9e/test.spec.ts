import { test, expect } from '@playwright/test';

test.describe('每日推送文章列表', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/dashboard', { waitUntil: 'domcontentloaded' });
  });

  test('环境验证: 页面加载成功', async ({ page }) => {
    await expect(page.getByTestId('page-container')).toBeVisible();
  });

  test('TC-002: 文章列表加载性能（响应时间）', async ({ page }) => {
    const startTime = await page.evaluate(() => performance.now());
    await page.reload({ waitUntil: 'domcontentloaded' });
    const endTime = await page.evaluate(() => performance.now());
    const loadTime = endTime - startTime;
    expect(loadTime).toBeLessThan(2000);
  });
});