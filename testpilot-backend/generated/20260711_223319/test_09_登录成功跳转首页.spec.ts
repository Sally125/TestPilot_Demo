import { test, expect } from '@playwright/test';

test('登录成功跳转首页', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('邮箱').fill('test@example.com');
  await page.getByLabel('密码').fill('password');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page).toHaveURL('http://localhost:3000');
  // 假设登录后页面包含用户信息元素，可根据实际情况调整选择器
  // await expect(page.getByText('用户信息')).toBeVisible();
});