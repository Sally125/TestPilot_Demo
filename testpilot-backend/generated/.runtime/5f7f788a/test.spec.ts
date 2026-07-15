import { test, expect } from '@playwright/test';

test.describe('每日推送 - 外部链接跳转', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
  const USERNAME = process.env.USERNAME || 'admin';
  const PASSWORD = process.env.PASSWORD || 'password';

  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await page.getByLabel('用户名').fill(USERNAME);
    await page.getByLabel('密码').fill(PASSWORD);
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
    // 确保页面有外部链接文章，为简化，假设第一篇文章是外部链接
  });

  test('验证点击外部链接文章在新标签页打开', async ({ page, context }) => {
    // 准备监听新标签页
    const pagePromise = context.waitForEvent('page');
    // 点击外部链接文章卡片（假设卡片上有indicator标识外部链接，或直接点击所有卡片中带特定属性的）
    // 这里假设第一个是外部链接，实际需要根据data-testid区分
    await page.getByTestId('article-card').first().click();
    // 等待新标签页出现
    const newPage = await pagePromise;
    await newPage.waitForLoadState('domcontentloaded');
    // 新标签页URL应为外部链接
    const newUrl = newPage.url();
    expect(newUrl).not.toContain(BASE_URL);
  });
});