import { test, expect } from '@playwright/test';

test('??????', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  const newTodo = page.getByPlaceholder('What needs to be done?');
  await newTodo.fill('??????');
  await newTodo.press('Enter');
  await expect(page.getByText('??????')).toBeVisible();
});