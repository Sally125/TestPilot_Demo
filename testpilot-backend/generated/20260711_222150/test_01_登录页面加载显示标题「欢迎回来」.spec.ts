import { test, expect } from '@playwright/test';

test('登录页面加载显示标题「欢迎回来」', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.getByText('欢迎回来')).toBeVisible();
});