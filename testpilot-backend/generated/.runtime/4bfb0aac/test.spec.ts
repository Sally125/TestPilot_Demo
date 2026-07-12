import { test, expect } from '@playwright/test';

test.describe('TodoMVC-标记完成与删除', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'domcontentloaded' });
  });

  test('标记待办完成并取消完成', async ({ page }) => {
    const todoText1 = '任务一';
    const todoText2 = '任务二';
    await page.getByPlaceholder('What needs to be done?').fill(todoText1);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByPlaceholder('What needs to be done?').fill(todoText2);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    const firstCheckbox = page.getByRole('listitem').filter({ hasText: todoText1 }).getByRole('checkbox');
    await firstCheckbox.check();
    await expect(firstCheckbox).toBeChecked();
    await firstCheckbox.uncheck();
    await expect(firstCheckbox).not.toBeChecked();
  });

  test('删除单个待办', async ({ page }) => {
    const todoText = '待删除任务';
    await page.getByPlaceholder('What needs to be done?').fill(todoText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    const todoItem = page.getByRole('listitem').filter({ hasText: todoText });
    await todoItem.hover();
    await todoItem.locator('.destroy').click();
    await expect(page.getByText(todoText)).not.toBeVisible();
  });

  test('批量清除已完成待办', async ({ page }) => {
    const todos = ['读书', '写作', '运动'];
    for (const text of todos) {
      await page.getByPlaceholder('What needs to be done?').fill(text);
      await page.getByPlaceholder('What needs to be done?').press('Enter');
    }
    await page.getByRole('listitem').filter({ hasText: todos[0] }).getByRole('checkbox').check();
    await page.getByRole('listitem').filter({ hasText: todos[1] }).getByRole('checkbox').check();
    await page.getByRole('button', { name: 'Clear completed' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(1);
    await expect(page.getByText(todos[2])).toBeVisible();
    await expect(page.getByText(todos[0])).not.toBeVisible();
    await expect(page.getByText(todos[1])).not.toBeVisible();
    await expect(page.getByText('1 item left')).toBeVisible();
  });
});