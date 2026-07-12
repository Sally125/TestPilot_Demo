import { test, expect } from '@playwright/test';

test.describe('考公大师-登录与导航', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
  });

  test('输入有效邮箱密码后登录成功跳转到首页', async ({ page }) => {
    // 注意：请使用有效的测试账号替换以下凭据
    const email = 'valid@test.com';
    const password = 'validpassword';
    await page.getByLabel('邮箱').fill(email);
    await page.getByLabel('密码').fill(password);
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL('http://localhost:3000');
  });

  test('点击注册链接跳转到注册页面', async ({ page }) => {
    await page.getByText('还没有账号？立即注册').click();
    await expect(page).toHaveURL(/register/);
  });
});