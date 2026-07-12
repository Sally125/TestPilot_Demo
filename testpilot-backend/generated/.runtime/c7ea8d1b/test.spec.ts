import { test, expect } from '@playwright/test';

test('??????', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  await expect(page.getByText('??????')).toBeVisible();
});