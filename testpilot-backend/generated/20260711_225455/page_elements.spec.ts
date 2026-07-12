import { test, expect } from '@playwright/test';

test.describe('考公大师-页面元素验证', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
  });

  test('页面标题显示欢迎回来', async ({ page }) => {
    await expect(page.getByText('欢迎回来')).toBeVisible();
  });

  test('邮箱输入框具有label和placeholder', async ({ page }) => {
    const emailInput = page.getByLabel('邮箱');
    await expect(emailInput).toBeVisible();
    await expect(emailInput).toHaveAttribute('placeholder', 'your@email.com');
  });

  test('密码输入框类型为password', async ({ page }) => {
    const passwordInput = page.getByLabel('密码');
    await expect(passwordInput).toBeVisible();
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('登录按钮文本为登录', async ({ page }) => {
    const loginButton = page.getByRole('button', { name: '登录' });
    await expect(loginButton).toBeVisible();
    await expect(loginButton).toHaveText('登录');
  });
});