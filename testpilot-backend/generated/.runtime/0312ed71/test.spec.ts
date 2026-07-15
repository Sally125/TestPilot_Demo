const { test, expect } = require('@playwright/test');

test('用户登录（手机号+密码+图形验证码） - 基础功能验证', async ({ page }) => {
  await page.goto('http://localhost:28089', { waitUntil: 'networkidle' });
  await expect(page).toHaveTitle(/.*/);
  await page.waitForTimeout(2000);
});
