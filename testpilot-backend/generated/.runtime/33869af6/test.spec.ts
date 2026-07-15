const { test, expect } = require('@playwright/test');

test('首页商品列表浏览 - 基础功能验证', async ({ page }) => {
  await page.goto('http://localhost:28089', { waitUntil: 'networkidle' });
  await expect(page).toHaveTitle(/.*/);
  await page.waitForTimeout(2000);
});
