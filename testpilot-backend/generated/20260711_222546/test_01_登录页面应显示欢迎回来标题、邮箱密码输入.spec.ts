import { test, expect } from '@playwright/test';

test('登录页面应显示欢迎回来标题、邮箱密码输入框及登录按钮等元素', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.getByText('欢迎回来')).toBeVisible();
  const emailInput = page.getByLabel('邮箱');
  await expect(emailInput).toBeVisible();
  await expect(emailInput).toHaveAttribute('placeholder', 'your@email.com');
  const passwordInput = page.getByLabel('密码');
  await expect(passwordInput).toBeVisible();
  await expect(passwordInput).toHaveAttribute('type', 'password');
  await expect(page.getByRole('button', { name: '登录' })).toBeVisible();
  await expect(page.getByText('还没有账号？立即注册')).toBeVisible();
});