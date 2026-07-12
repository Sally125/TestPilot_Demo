import { test, expect } from '@playwright/test';

test('邮箱输入框元素验证 - 属性和占位符', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.getByLabel('邮箱')).toBeVisible();
  await expect(page.getByPlaceholder('your@email.com')).toBeVisible();
});