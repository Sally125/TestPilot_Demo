import { test, expect } from '@playwright/test';

test.describe('考公大师-登录与导航', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
  });

  test('使用有效账号登录成功跳转到首页', async ({ page }) => {
    await page.getByLabel('邮箱').fill('1475362884@qq.com');
    await page.getByLabel('密码').fill('h13778093158');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL('http://localhost:3000');
  });

  test('点击注册链接跳转到注册页', async ({ page }) => {
    await page.getByText('还没有账号？立即注册').click();
    await expect(page).toHaveURL(/register/);
  });
});