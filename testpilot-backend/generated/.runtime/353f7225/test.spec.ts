import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办-多任务添加与计数', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('连续添加三个待办并验证', async ({ page }) => {
    const todos = ['任务1', '任务2', '任务3'];
    for (const todo of todos) {
      await page.getByPlaceholder('What needs to be done?').fill(todo);
      await page.getByPlaceholder('What needs to be done?').press('Enter');
    }
    for (const todo of todos) {
      await expect(page.getByText(todo)).toBeVisible();
    }
  });

  test('验证待办计数显示正确', async ({ page }) => {
    const todos = ['任务1', '任务2', '任务3'];
    for (const todo of todos) {
      await page.getByPlaceholder('What needs to be done?').fill(todo);
      await page.getByPlaceholder('What needs to be done?').press('Enter');
    }
    await expect(page.getByText('3 items left')).toBeVisible();
  });
});