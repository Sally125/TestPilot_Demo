import { test, expect } from '@playwright/test';

test('登录按钮存在且文本正确', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.getByRole('button', { name: '登录' })).toBeVisible();
});