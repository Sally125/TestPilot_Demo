import { test, expect } from '@playwright/test';

test.describe('TodoMVC-过滤与导航', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('统计信息显示正确', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Task 1');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByPlaceholder('What needs to be done?').fill('Task 2');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText('2 items left')).toBeVisible();
  });

  test('Active过滤只显示未完成事项', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Active task');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByPlaceholder('What needs to be done?').fill('Completed task');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByRole('checkbox', { name: 'Toggle Todo' }).nth(1).check();
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.getByText('Active task')).toBeVisible();
  });

  test('Completed过滤只显示已完成事项', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Completed task');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByRole('checkbox', { name: 'Toggle Todo' }).check();
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.getByText('Completed task')).toBeVisible();
  });
});