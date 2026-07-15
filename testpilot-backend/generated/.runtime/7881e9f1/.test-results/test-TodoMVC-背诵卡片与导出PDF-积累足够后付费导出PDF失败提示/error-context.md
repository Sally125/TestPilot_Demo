# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> TodoMVC-背诵卡片与导出PDF >> 积累足够后付费导出PDF失败提示
- Location: testpilot-backend\generated\.runtime\7881e9f1\test.spec.ts:19:7

# Error details

```
Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
Call log:
  - navigating to "未提供", waiting until "domcontentloaded"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('TodoMVC-背诵卡片与导出PDF', () => {
  4  |   test.beforeEach(async ({ page }) => {
> 5  |     await page.goto('未提供', { waitUntil: 'domcontentloaded' });
     |                ^ Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
  6  |     // 登录操作
  7  |     await page.getByLabel('邮箱').fill('test@example.com');
  8  |     await page.getByLabel('密码').fill('password123');
  9  |     await page.getByRole('button', { name: '登录' }).click();
  10 |     await expect(page).toHaveURL('未提供');
  11 |   });
  12 | 
  13 |   test('每日显示5张背诵卡片', async ({ page }) => {
  14 |     await page.getByTestId('card-container').waitFor();
  15 |     const cards = page.getByTestId('card-item');
  16 |     await expect(cards).toHaveCount(5);
  17 |   });
  18 | 
  19 |   test('积累足够后付费导出PDF失败提示', async ({ page }) => {
  20 |     // 假设积累足够后会出现导出按钮
  21 |     await page.getByTestId('export-pdf-button').click();
  22 |     // 模拟付费失败场景（例如余额不足）
  23 |     await page.getByTestId('pay-button').click();
  24 |     await expect(page.getByText(/支付失败|余额不足/)).toBeVisible();
  25 |   });
  26 | });
```