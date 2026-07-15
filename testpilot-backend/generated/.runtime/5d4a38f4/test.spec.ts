import { test, expect } from '@playwright/test';

test.describe('TodoMVC-删除待办与按状态过滤', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    // 添加三个待办，并标记第二个为已完成
    const input = page.getByPlaceholder('What needs to be done?');
    for (const text of ['任务A', '任务B', '任务C']) {
      await input.fill(text);
      await input.press('Enter');
    }
    // 标记任务B为完成
    await page.getByTestId('todo-item').filter({ hasText: '任务B' }).getByRole('checkbox').check();
  });

  test('删除单个待办', async ({ page }) => {
    const todo = page.getByTestId('todo-item').filter({ hasText: '任务A' });
    await expect(todo).toBeVisible();
    // 悬停后点击删除按钮
    await todo.hover();
    await todo.locator('button.destroy').click();
    await expect(todo).not.toBeVisible();
  });

  test('按状态过滤列表并验证计数', async ({ page }) => {
    // 验证初始计数显示 3 items left
    await expect(page.getByText('3 items left')).toBeVisible();
    // 点击「已完成」
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.getByTestId('todo-item')).toHaveCount(1);
    await expect(page.getByTestId('todo-item').filter({ hasText: '任务B' })).toBeVisible();
    await expect(page.getByText('3 items left')).not.toBeVisible();
    // 点击「待办」
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.getByTestId('todo-item')).toHaveCount(2);
    await expect(page.getByTestId('todo-item').filter({ hasText: '任务A' })).toBeVisible();
    // 点击「所有」
    await page.getByRole('link', { name: 'All' }).click();
    await expect(page.getByTestId('todo-item')).toHaveCount(3);
  });

  test('清除所有已完成待办', async ({ page }) => {
    // 点击清除已完成按钮
    await page.getByRole('button', { name: 'Clear completed' }).click();
    await expect(page.getByTestId('todo-item')).toHaveCount(2);
    await expect(page.getByTestId('todo-item').filter({ hasText: '任务B' })).not.toBeVisible();
    // 验证底部计数更新
    await expect(page.getByText('2 items left')).toBeVisible();
  });
});