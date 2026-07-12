import { test, expect } from '@playwright/test';

test('表单验证 - 邮箱为空时的错误提示', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('密码').fill('password123');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText('请输入邮箱')).toBeVisible();
});