import { test, expect } from '@playwright/test';

test('登录按钮文本为「登录」且背景为蓝色', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  const loginButton = page.getByRole('button', { name: '登录' });
  await expect(loginButton).toHaveText('登录');
  await expect(loginButton).toHaveCSS('background-color', 'rgb(0, 0, 255)');
});