import { test, expect } from '@playwright/test';

test.describe('TodoMVC-按状态过滤列表', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    await page.getByPlaceholder('What needs to be done?').fill('待办1');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByPlaceholder('What needs to be done?').fill('待办2');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.getByPlaceholder('What needs to be done?').fill('待办3');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await page.locator('li').filter({ hasText: '待办2' }).locator('input[type="checkbox"]').click();
  });

  test('过滤【待办】列表', async ({ page }) => {
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.locator('ul.todo-list li')).toHaveCount(2);
    await expect(page.locator('li').filter({ hasText: '待办1' })).toBeVisible();
    await expect(page.locator('li').filter({ hasText: '待办3' })).toBeVisible();
    await expect(page.locator('li').filter({ hasText: '待办2' })).not.toBeVisible();
    await expect(page.locator('.todo-count')).toHaveText('2 items left');
  });

  test('过滤【已完成】列表', async ({ page }) => {
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.locator('ul.todo-list li')).toHaveCount(1);
    await expect(page.locator('li').filter({ hasText: '待办2' })).toBeVisible();
    await expect(page.locator('li').filter({ hasText: '待办1' })).not.toBeVisible();
  });

  test('切换回【全部】列表', async ({ page }) => {
    await page.getByRole('link', { name: 'Active' }).click();
    await expect(page.locator('ul.todo-list li')).toHaveCount(2);
    await page.getByRole('link', { name: 'All' }).click();
    await expect(page.locator('ul.todo-list li')).toHaveCount(3);
  });
});