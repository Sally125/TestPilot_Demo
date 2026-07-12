import { test, expect } from '@playwright/test';

test.describe('TodoMVC-按状态过滤', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Task1');
    await page.keyboard.press('Enter');
    await input.fill('Task2');
    await page.keyboard.press('Enter');
    await input.fill('Task3');
    await page.keyboard.press('Enter');
    await page.getByRole('listitem').filter({ hasText: 'Task1' }).getByRole('checkbox').click();
  });

  test('过滤显示待办（Active）', async ({ page }) => {
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(2);
    await expect(page.getByText('Task1')).toBeHidden();
    await expect(page.getByText('Task2')).toBeVisible();
    await expect(page.getByText('Task3')).toBeVisible();
    await expect(page.getByText('2 items left')).toBeVisible();
  });

  test('过滤显示已完成（Completed）', async ({ page }) => {
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(1);
    await expect(page.getByText('Task1')).toBeVisible();
    await expect(page.getByText('Task2')).toBeHidden();
    await expect(page.getByText('2 items left')).toBeVisible();
  });

  test('显示所有待办（All）', async ({ page }) => {
    await page.getByRole('link', { name: 'All' }).click();
    await expect(page.getByRole('listitem')).toHaveCount(3);
    await expect(page.getByText('Task1')).toBeVisible();
    await expect(page.getByText('Task2')).toBeVisible();
    await expect(page.getByText('Task3')).toBeVisible();
    await expect(page.getByText('2 items left')).toBeVisible();
  });

  test('在过滤状态下标记完成', async ({ page }) => {
    await page.getByRole('link', { name: 'Active' }).click();
    const task2Checkbox = page.getByRole('listitem').filter({ hasText: 'Task2' }).getByRole('checkbox');
    await task2Checkbox.click();
    await expect(page.getByRole('listitem')).toHaveCount(1);
    await expect(page.getByText('Task2')).toBeHidden();
    await expect(page.getByText('Task3')).toBeVisible();
  });
});