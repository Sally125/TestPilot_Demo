import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办项', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('学习Playwright');
    await input.press('Enter');
    await expect(page.getByText('学习Playwright')).toBeVisible();
    await expect(page.locator('.todo-count')).toHaveText('1 item left');
  });

  test('添加空文本或仅空格不创建', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('');
    await input.press('Enter');
    await expect(page.locator('.todo-list li')).toHaveCount(0);
    await input.fill('   ');
    await input.press('Enter');
    await expect(page.locator('.todo-list li')).toHaveCount(0);
  });

  test('添加超长文本和特殊字符', async ({ page }) => {
    const longText = 'a'.repeat(200);
    const specialText = '<script>alert("xss")</script>';
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill(longText);
    await input.press('Enter');
    await expect(page.getByText(longText)).toBeVisible();
    await input.fill(specialText);
    await input.press('Enter');
    await expect(page.getByText(specialText)).toBeVisible();
    await expect(page.locator('.todo-count')).toHaveText('2 items left');
  });
});