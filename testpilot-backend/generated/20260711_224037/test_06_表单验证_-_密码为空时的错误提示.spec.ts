import { test, expect } from '@playwright/test';

test('表单验证 - 密码为空时的错误提示', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('邮箱').fill('test@example.com');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText('请输入密码')).toBeVisible();
});