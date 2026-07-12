import { test, expect } from '@playwright/test';

test('成功登录并跳转首页', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('邮箱').fill('testuser@example.com');
  await page.getByLabel('密码').fill('TestPass123');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page).toHaveURL('http://localhost:3000');
});