import { test, expect } from '@playwright/test';

test.describe('TodoMVC - 按状态过滤', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('切换过滤显示正确列表', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('待办1');
    await input.press('Enter');
    await input.fill('待办2');
    await input.press('Enter');
    await input.fill('待办3');
    await input.press('Enter');

    // 完成待办1和待办2
    const item1 = page.getByRole('listitem').filter({ hasText: '待办1' });
    const item2 = page.getByRole('listitem').filter({ hasText: '待办2' });
    await item1.getByRole('checkbox').check();
    await item2.getByRole('checkbox').check();

    // 点击 Active
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(1);
    await expect(page.getByText('待办3')).toBeVisible();

    // 点击 Completed
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(2);
  });

  test('过滤状态下操作', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('任务1');
    await input.press('Enter');
    await input.fill('任务2');
    await input.press('Enter');

    // 完成任务1
    const task1 = page.getByRole('listitem').filter({ hasText: '任务1' });
    await task1.getByRole('checkbox').check();

    // 切换到 Active
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(1);
    await expect(page.getByText('任务2')).toBeVisible();

    // 在 Active 下完成任务2
    const task2 = page.getByRole('listitem').filter({ hasText: '任务2' });
    await task2.getByRole('checkbox').check();

    // Active 列表为空
    await expect(page.getByRole('listitem')).toHaveCount(0);

    // 切换到 Completed 应看到两个任务
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(2);
  });
});