import { test, expect } from '@playwright/test';

test('表单验证 - 邮箱密码均为空时的错误提示', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByRole('button', { name: '登录' }).click();
  // 假设同时提示两个错误
  await expect(page.getByText('请输入邮箱')).toBeVisible();
  await expect(page.getByText('请输入密码')).toBeVisible();
});