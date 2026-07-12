import { test, expect } from '@playwright/test';

test.describe('考公大师-登录与导航', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
  });

  test('登录成功并跳转首页', async ({ page }) => {
    // 使用有效测试账号（请确保该账号在测试环境中存在）
    await page.getByLabel('邮箱').fill('test@kaogong.com');
    await page.getByLabel('密码').fill('123456');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL('http://localhost:3000');
  });

  test('登录失败：无效密码', async ({ page }) => {
    await page.getByLabel('邮箱').fill('test@kaogong.com');
    await page.getByLabel('密码').fill('wrongpassword');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.getByText(/密码错误|密码/)).toBeVisible();
  });

  test('登录失败：无效邮箱', async ({ page }) => {
    await page.getByLabel('邮箱').fill('notexist@test.com');
    await page.getByLabel('密码').fill('anypassword');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page.getByText(/账号不存在|邮箱/)).toBeVisible();
  });

  test('注册链接跳转', async ({ page }) => {
    await page.getByText('还没有账号？立即注册').click();
    await expect(page).toHaveURL(/register/);
  });
});