import { test, expect } from '@playwright/test';

test('空邮箱点击登录显示错误提示', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('密码').fill('somepassword');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText('请填写邮箱')).toBeVisible();
});