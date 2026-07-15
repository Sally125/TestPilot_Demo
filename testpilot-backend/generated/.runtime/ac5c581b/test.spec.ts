import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('学习 Playwright');
    await input.press('Enter');
    await expect(page.getByText('学习 Playwright')).toBeVisible();
    await expect(page.getByText('1 item left')).toBeVisible();
  });

  test('空输入不添加待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('');
    await input.press('Enter');
    await expect(page.getByText('0 items left')).toBeVisible();
    // 通过计数确保没有新增，也可检查列表项数量
  });
});