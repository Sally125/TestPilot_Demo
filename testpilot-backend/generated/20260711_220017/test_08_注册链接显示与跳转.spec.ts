import { test, expect } from '@playwright/test';

test('注册链接显示与跳转', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  const registerLink = page.getByText('还没有账号？立即注册');
  await expect(registerLink).toBeVisible();
  await registerLink.click();
  await expect(page).toHaveURL(/register/);
});