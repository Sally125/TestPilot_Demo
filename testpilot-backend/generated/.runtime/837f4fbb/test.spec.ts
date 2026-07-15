import { test, expect } from '@playwright/test';

test.describe('TodoMVC-高亮与操作菜单', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('未提供', { waitUntil: 'domcontentloaded' });
    // 进入精读页面
    await page.getByTestId('article-item').first().click();
    await expect(page.getByTestId('original-article-tab')).toBeVisible();
  });

  test('点击高亮文本弹出操作菜单并可执行操作', async ({ page }) => {
    // 点击一个高亮区域（假设为红色高亮）
    await page.getByTestId('highlight-red').first().click();
    await expect(page.getByTestId('operation-menu')).toBeVisible();
    await page.getByTestId('menu-copy').click();
    // 验证复制成功提示
    await expect(page.getByText(/复制成功|已复制/)).toBeVisible();
  });

  test('点击非高亮文本区域不弹出菜单', async ({ page }) => {
    // 点击一段普通文本
    await page.getByTestId('normal-text').first().click();
    await expect(page.getByTestId('operation-menu')).not.toBeVisible();
  });
});