import { test, expect } from '@playwright/test';

test('邮箱和密码均为空时点击登录应提示错误', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText(/邮箱|密码/)).toBeVisible();
});