import { test, expect } from '@playwright/test';

test('注册链接存在且可跳转', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  const registerLink = page.getByText(/立即注册|还没有账号/);
  await expect(registerLink).toBeVisible();
  await registerLink.click();
  await expect(page).toHaveURL(/\/register/);
});