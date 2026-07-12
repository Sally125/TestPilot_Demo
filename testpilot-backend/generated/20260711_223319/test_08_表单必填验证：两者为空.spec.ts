import { test, expect } from '@playwright/test';

test('表单必填验证：两者为空', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText(/邮箱不能为空|密码不能为空|请输入邮箱|请输入密码/).first()).toBeVisible();
});