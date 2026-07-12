import { test, expect } from '@playwright/test';

test('有效凭据登录成功并跳转首页', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  // 注意：需要替换为有效的测试账号和密码
  await page.getByLabel('邮箱').fill('test@example.com');
  await page.getByLabel('密码').fill('password123');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page).toHaveURL('http://localhost:3000');
  await expect(page.locator('body')).toBeVisible();
});