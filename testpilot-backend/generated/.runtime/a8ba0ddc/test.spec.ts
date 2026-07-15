import { test, expect } from '@playwright/test';

test.describe('TodoMVC - 添加待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('测试任务');
    await input.press('Enter');
    const todoItem = page.getByText('测试任务');
    await expect(todoItem).toBeVisible();
    const todoLi = page.getByRole('listitem').filter({ hasText: '测试任务' });
    await expect(todoLi).not.toHaveClass(/completed/);
  });

  test('空输入不创建', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('   ');
    await input.press('Enter');
    const todos = page.getByRole('listitem');
    await expect(todos).toHaveCount(0);
  });

  test('超长文本', async ({ page }) => {
    const longText = 'a'.repeat(1000);
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill(longText);
    await input.press('Enter');
    const todoItem = page.getByText(longText);
    await expect(todoItem).toBeVisible();
  });

  test('特殊字符和HTML注入', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill(`<script>alert('xss')</script>`);
    await input.press('Enter');
    const todoItem = page.getByText(`<script>alert('xss')</script>`);
    await expect(todoItem).toBeVisible();
  });
});