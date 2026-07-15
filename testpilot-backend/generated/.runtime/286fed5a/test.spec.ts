import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('测试待办');
    await input.press('Enter');
    await expect(input).toBeEmpty();
    await expect(page.getByText('测试待办')).toBeVisible();
    await expect(page.getByText('1 item left')).toBeVisible();
  });

  test('添加空文本被拒绝', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('   ');
    await input.press('Enter');
    await expect(page.locator('.todo-list li')).toHaveCount(0);
  });

  test('添加包含特殊字符的文本', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    const specialText = '<script>alert(\"xss\")</script>';
    await input.fill(specialText);
    await input.press('Enter');
    await expect(page.getByText(specialText)).toBeVisible();
  });
});