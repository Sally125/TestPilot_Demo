import { test, expect } from '@playwright/test';

test('登录按钮背景色为蓝色', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  const button = page.getByRole('button', { name: '登录' });
  await expect(button).toHaveCSS('background-color', /^(rgb\(0, 123, 255\)|#007bff)/i);
});