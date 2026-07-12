import { test, expect } from '@playwright/test';

test('登录页面可访问并显示欢迎标题', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.getByText('欢迎回来')).toBeVisible();
});