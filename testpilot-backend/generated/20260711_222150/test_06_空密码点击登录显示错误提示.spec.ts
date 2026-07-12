import { test, expect } from '@playwright/test';

test('空密码点击登录显示错误提示', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('邮箱').fill('test@example.com');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText('请填写密码')).toBeVisible();
});