import { test, expect } from '@playwright/test';

test.describe('TodoMVC-背诵卡片与导出PDF', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('未提供', { waitUntil: 'domcontentloaded' });
    // 登录操作
    await page.getByLabel('邮箱').fill('test@example.com');
    await page.getByLabel('密码').fill('password123');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL('未提供');
  });

  test('每日显示5张背诵卡片', async ({ page }) => {
    await page.getByTestId('card-container').waitFor();
    const cards = page.getByTestId('card-item');
    await expect(cards).toHaveCount(5);
  });

  test('积累足够后付费导出PDF失败提示', async ({ page }) => {
    // 假设积累足够后会出现导出按钮
    await page.getByTestId('export-pdf-button').click();
    // 模拟付费失败场景（例如余额不足）
    await page.getByTestId('pay-button').click();
    await expect(page.getByText(/支付失败|余额不足/)).toBeVisible();
  });
});