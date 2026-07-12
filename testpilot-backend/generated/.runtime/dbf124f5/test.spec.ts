import { test, expect } from '@playwright/test';
test.describe('TodoMVC-标记待办完成', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('待办一');
    await input.press('Enter');
    await input.fill('待办二');
    await input.press('Enter');
  });
  test('标记一个待办为完成', async ({ page }) => {
    const firstCheckbox = page.getByRole('listitem').filter({ hasText: '待办一' }).getByRole('checkbox');
    await firstCheckbox.click();
    await expect(firstCheckbox).toBeChecked();
    await expect(page.getByText('1 item left')).toBeVisible();
  });
  test('切换待办状态从完成到未完成', async ({ page }) => {
    const firstCheckbox = page.getByRole('listitem').filter({ hasText: '待办一' }).getByRole('checkbox');
    await firstCheckbox.click();
    await firstCheckbox.click();
    await expect(firstCheckbox).not.toBeChecked();
    await expect(page.getByText('2 items left')).toBeVisible();
  });
});