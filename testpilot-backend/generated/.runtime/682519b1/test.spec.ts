import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加任务-基本功能', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('添加任务-正常输入', async ({ page }) => {
    const taskText = '写测试用例';
    await page.getByPlaceholder('What needs to be done?').fill(taskText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(taskText)).toBeVisible();
  });

  test('添加任务-必填字段校验', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    const todoItems = page.locator('.todo-list li');
    await expect(todoItems).toHaveCount(0);
  });

  test('添加任务-特殊字符输入', async ({ page }) => {
    const taskText = '<script>alert("xss")</script>';
    await page.getByPlaceholder('What needs to be done?').fill(taskText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(taskText)).toBeVisible();
  });
});