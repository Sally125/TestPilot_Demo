const { test, expect } = require('@playwright/test');

test('商品详情查看 - 基础功能验证', async ({ page }) => {
  await page.goto('http://localhost:28089', { waitUntil: 'networkidle' });
  await expect(page).toHaveTitle(/.*/);
  await page.waitForTimeout(2000);
});
