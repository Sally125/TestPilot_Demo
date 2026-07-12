import { test, expect } from '@playwright/test';

test('表单必填验证：邮箱为空', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByLabel('密码').fill('somepassword');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText(/邮箱不能为空|请输入邮箱/)).toBeVisible();
});