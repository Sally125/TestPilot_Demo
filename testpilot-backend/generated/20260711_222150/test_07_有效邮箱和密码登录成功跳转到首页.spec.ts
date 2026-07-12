import { test, expect } from '@playwright/test';

test('有效邮箱和密码登录成功跳转到首页', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('邮箱').fill('test@example.com');
  await page.getByLabel('密码').fill('password123');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page).toHaveURL('http://localhost:3000');
});