import { test, expect } from '@playwright/test';

test.describe('TodoMVC-标记完成与删除', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Task1');
    await page.keyboard.press('Enter');
    await input.fill('Task2');
    await page.keyboard.press('Enter');
    await input.fill('Task3');
    await page.keyboard.press('Enter');
  });

  test('标记单个待办为完成', async ({ page }) => {
    const task1Checkbox = page.getByRole('listitem').filter({ hasText: 'Task1' }).getByRole('checkbox');
    await task1Checkbox.click();
    await expect(task1Checkbox).toBeChecked();
    await expect(page.getByText('2 items left')).toBeVisible();
  });

  test('取消标记完成', async ({ page }) => {
    const task1Checkbox = page.getByRole('listitem').filter({ hasText: 'Task1' }).getByRole('checkbox');
    await task1Checkbox.click();
    await expect(task1Checkbox).toBeChecked();
    await task1Checkbox.click();
    await expect(task1Checkbox).not.toBeChecked();
    await expect(page.getByText('3 items left')).toBeVisible();
  });

  test('删除单个待办', async ({ page }) => {
    const task2Item = page.getByRole('listitem').filter({ hasText: 'Task2' });
    await task2Item.hover();
    await task2Item.getByRole('button').click();
    await expect(page.getByRole('listitem')).toHaveCount(2);
    await expect(page.getByText('2 items left')).toBeVisible();
  });

  test('清除所有已完成', async ({ page }) => {
    const task1Checkbox = page.getByRole('listitem').filter({ hasText: 'Task1' }).getByRole('checkbox');
    const task2Checkbox = page.getByRole('listitem').filter({ hasText: 'Task2' }).getByRole('checkbox');
    await task1Checkbox.click();
    await task2Checkbox.click();
    await page.getByRole('button', { name: 'Clear completed' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(1);
    await expect(page.getByText('1 item left')).toBeVisible();
  });
});