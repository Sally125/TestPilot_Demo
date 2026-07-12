import { test, expect } from '@playwright/test';

test('邮箱为空时点击登录显示必填错误', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('密码').fill('123456');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText(/邮箱/)).toBeVisible();
});