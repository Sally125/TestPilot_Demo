import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办与标记完成', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办并标记完成再取消', async ({ page }) => {
    // 添加待办
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('测试待办');
    await input.press('Enter');
    // 验证待办出现
    const todoItem = page.getByTestId('todo-item').filter({ hasText: '测试待办' });
    await expect(todoItem).toBeVisible();
    // 验证未完成（没有 line-through）
    await expect(todoItem.locator('label')).not.toHaveCSS('text-decoration-line', 'line-through');
    // 标记完成
    await todoItem.getByRole('checkbox').check();
    await expect(todoItem.locator('label')).toHaveCSS('text-decoration-line', 'line-through');
    // 取消完成
    await todoItem.getByRole('checkbox').uncheck();
    await expect(todoItem.locator('label')).not.toHaveCSS('text-decoration-line', 'line-through');
  });

  test('输入空文本或仅空格时不应创建待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    // 空文本
    await input.fill('');
    await input.press('Enter');
    await expect(page.getByTestId('todo-item')).not.toBeVisible();
    // 仅空格
    await input.fill('   ');
    await input.press('Enter');
    await expect(page.getByTestId('todo-item')).not.toBeVisible();
  });

  test('添加多个待办并全选/取消全选', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    for (const text of ['任务1', '任务2', '任务3']) {
      await input.fill(text);
      await input.press('Enter');
    }
    // 全选
    await page.getByRole('checkbox', { name: 'Mark all as complete' }).check();
    await expect(page.getByTestId('todo-item').first().locator('label')).toHaveCSS('text-decoration-line', 'line-through');
    // 取消全选
    await page.getByRole('checkbox', { name: 'Mark all as complete' }).uncheck();
    await expect(page.getByTestId('todo-item').first().locator('label')).not.toHaveCSS('text-decoration-line', 'line-through');
  });
});