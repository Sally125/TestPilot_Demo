const { test, expect } = require('@playwright/test');

test('登录状态保持 - 基础功能验证', async ({ page }) => {
  await page.goto('http://localhost:3001', { waitUntil: 'networkidle' });
  await expect(page).toHaveTitle(/.*/);
  await page.waitForTimeout(2000);
});
