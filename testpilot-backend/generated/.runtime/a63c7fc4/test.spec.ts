import { test, expect } from '@playwright/test';

test.describe('考公大师-页面元素验证', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
  });

  test('页面标题显示欢迎回来', async ({ page }) => {
    await expect(page.getByText('欢迎回来')).toBeVisible();
  });

  test('邮箱输入框存在且占位符正确', async ({ page }) => {
    await expect(page.getByLabel('邮箱')).toHaveAttribute('placeholder', 'your@email.com');
  });

  test('密码输入框存在且类型为password', async ({ page }) => {
    await expect(page.getByLabel('密码')).toHaveAttribute('type', 'password');
  });

  test('登录按钮文本正确且可点击', async ({ page }) => {
    await expect(page.getByRole('button', { name: '登录' })).toBeEnabled();
  });

  test('注册链接文本可见', async ({ page }) => {
    await expect(page.getByText('还没有账号？立即注册')).toBeVisible();
  });
});