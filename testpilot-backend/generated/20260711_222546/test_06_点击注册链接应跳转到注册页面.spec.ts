import { test, expect } from '@playwright/test';

test('点击注册链接应跳转到注册页面', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByText('还没有账号？立即注册').click();
  await expect(page).toHaveURL(/\/register/);
});