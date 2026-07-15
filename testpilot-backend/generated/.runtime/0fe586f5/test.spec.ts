import { test, expect } from '@playwright/test';

test.describe('TodoMVC-增加待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办事项', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('测试待办');
    await input.press('Enter');
    await expect(page.getByText('测试待办')).toBeVisible();
    await expect(page.getByText(/1 item left/)).toBeVisible();
  });

  test('输入空文本不能添加待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('');
    await input.press('Enter');
    await expect(page.locator('.todo-list li')).toHaveCount(0);
    await expect(page.getByText(/0 items left/)).toBeVisible();
  });

  test('输入超长文本和特殊字符', async ({ page }) => {
    const longText = 'a'.repeat(1000) + '<script>alert("xss")</script>';
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill(longText);
    await input.press('Enter');
    await expect(page.locator('.todo-list li')).toHaveCount(1);
    await expect(page.getByText(/1 item left/)).toBeVisible();
  });
});