import { test, expect } from '@playwright/test';

test('密码输入框存在且属性正确', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  const passwordInput = page.getByLabel('密码');
  await expect(passwordInput).toBeVisible();
  await expect(passwordInput).toHaveAttribute('type', 'password');
});