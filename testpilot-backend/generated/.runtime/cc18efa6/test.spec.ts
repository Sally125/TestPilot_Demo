import { test, expect } from '@playwright/test';

test.describe('TodoMVC-添加待办', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Buy milk');
    await page.keyboard.press('Enter');
    await expect(page.getByText('Buy milk')).toBeVisible();
    await expect(page.getByText('1 item left')).toBeVisible();
  });

  test('空输入不添加', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('   ');
    await page.keyboard.press('Enter');
    await expect(page.getByRole('listitem')).toHaveCount(0);
  });

  test('添加特殊字符不被转义', async ({ page }) => {
    const special = '<b>HTML</b>';
    await page.getByPlaceholder('What needs to be done?').fill(special);
    await page.keyboard.press('Enter');
    await expect(page.getByRole('listitem').filter({ hasText: special })).toHaveCount(1);
    await expect(page.getByRole('listitem').filter({ hasText: special })).toContainText(special);
  });
});