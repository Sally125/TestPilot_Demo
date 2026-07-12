import { test, expect } from '@playwright/test';

test('邮箱输入框显示标签和占位符', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  const emailInput = page.getByLabel('邮箱');
  await expect(emailInput).toBeVisible();
  await expect(emailInput).toHaveAttribute('placeholder', 'your@email.com');
});