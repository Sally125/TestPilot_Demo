import { test, expect } from '@playwright/test';

test.describe('每日推送 - 下拉刷新', () => {
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

  test('验证下拉刷新功能正常', async ({ page }) => {
    // 模拟后端新增一篇文章：通过route在刷新时返回新数据
    await page.route('**/api/articles*', async route => {
      // 每次刷新返回包含新文章的列表
      const articles = [
        { id: 99, title: '最新文章', summary: '新摘要', time: '2025-03-11' },
        { id: 1, title: '原有文章', summary: '旧摘要', time: '2025-03-10' }
      ];
      await route.fulfill({ status: 200, body: JSON.stringify({ articles, hasMore: false }) });
    });
    // 执行下拉刷新（假设通过点击刷新按钮或手势）
    const refreshButton = page.getByTestId('refresh-button');
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
    } else {
      // 模拟下拉手势（需在移动端或通过touch事件）
      await page.evaluate(() => {
        const element = document.querySelector('[data-testid="article-list"]');
        if(element) {
          const startY = 0;
          const endY = 300;
          const startEvent = new TouchEvent('touchstart', { touches: [{ clientX: 0, clientY: startY }] });
          const moveEvent = new TouchEvent('touchmove', { touches: [{ clientX: 0, clientY: endY }] });
          const endEvent = new TouchEvent('touchend', { changes: [{ clientX: 0, clientY: endY }] });
          element.dispatchEvent(startEvent);
          element.dispatchEvent(moveEvent);
          element.dispatchEvent(endEvent);
        }
      });
    }
    // 等待刷新完成，新文章出现在列表最上方
    const firstArticle = page.getByTestId('article-card').first();
    await expect(firstArticle.getByTestId('article-title')).toHaveText('最新文章');
  });
});