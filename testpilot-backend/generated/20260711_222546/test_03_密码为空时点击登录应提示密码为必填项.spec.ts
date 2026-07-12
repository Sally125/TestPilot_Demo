import { test, expect } from '@playwright/test';

test('密码为空时点击登录应提示密码为必填项', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('邮箱').fill('test@example.com');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText(/密码/)).toBeVisible();
});