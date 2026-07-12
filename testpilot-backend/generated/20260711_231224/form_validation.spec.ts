import { test, expect } from '@playwright/test';

test.describe('考公大师-表单验证', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login', { waitUntil: 'domcontentloaded' });
  });

  test('邮箱为空时点击登录显示错误提示', async ({ page }) => {
    await page.getByLabel('密码').fill('somepassword');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.getByText(/邮箱|必填/)).toBeVisible();
  });

  test('密码为空时点击登录显示错误提示', async ({ page }) => {
    await page.getByLabel('邮箱').fill('test@example.com');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.getByText(/密码|必填/)).toBeVisible();
  });

  test('邮箱和密码均为空时点击登录显示双错误', async ({ page }) => {
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.getByText(/邮箱|必填/)).toBeVisible();
    await expect(page.getByText(/密码|必填/)).toBeVisible();
  });
});