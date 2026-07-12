import { test, expect } from '@playwright/test';

test('注册链接文本验证 - 文本内容显示正确', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.getByText('还没有账号？立即注册')).toBeVisible();
});