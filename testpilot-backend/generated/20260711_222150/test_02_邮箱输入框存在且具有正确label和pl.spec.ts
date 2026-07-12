import { test, expect } from '@playwright/test';

test('邮箱输入框存在且具有正确label和placeholder', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.getByLabel('邮箱')).toBeVisible();
  await expect(page.getByPlaceholder('your@email.com')).toBeVisible();
});