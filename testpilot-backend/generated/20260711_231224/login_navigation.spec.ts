import { test, expect } from '@playwright/test';

test.describe('考公大师-登录与导航', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login', { waitUntil: 'domcontentloaded' });
  });

  test('使用有效账号登录成功跳转到首页', async ({ page }) => {
    await page.getByLabel('邮箱').fill('1475362884@qq.com');
    await page.getByLabel('密码').fill('h13778093158');
    await page.getByRole('button', { name: '登录' }).click();
    await page.waitForTimeout(2000);
    const currentUrl = page.url();
    if (currentUrl.includes('login')) {
      const errorMessages = await page.locator('body').textContent();
      console.log(`登录失败，当前URL: ${currentUrl}`);
      console.log(`页面内容: ${errorMessages?.substring(0, 500)}`);
    }
    await expect(page).toHaveURL('http://localhost:3000');
  });

  test('点击注册链接跳转到注册页', async ({ page }) => {
    await page.getByRole('link', { name: '立即注册' }).click();
    await expect(page).toHaveURL(/register/);
  });
});