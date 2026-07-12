import { test, expect } from '@playwright/test';

test('无效凭据登录应提示错误', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('邮箱').fill('nonexistent@example.com');
  await page.getByLabel('密码').fill('wrongpassword');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText(/错误|失败/)).toBeVisible();
  await expect(page).toHaveURL('http://localhost:3000/login');
});