import { test, expect } from '@playwright/test';

test('邮箱格式校验', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  const emailInput = page.getByLabel('邮箱');
  await emailInput.fill('abc');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText(/邮箱/)).toBeVisible();
});