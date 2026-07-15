# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test.spec.ts >> 每日推送 - 外部链接跳转 >> 验证点击外部链接文章在新标签页打开
- Location: testpilot-backend\generated\.runtime\5f7f788a\test.spec.ts:17:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: locator.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByLabel('用户名')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e4]:
    - generic [ref=e5]:
      - heading "欢迎回来" [level=1] [ref=e6]
      - paragraph [ref=e7]: 登录考公大师，继续你的备考之旅
    - generic [ref=e8]:
      - generic [ref=e9]:
        - generic [ref=e10]: 邮箱
        - textbox "邮箱" [ref=e11]:
          - /placeholder: your@email.com
      - generic [ref=e12]:
        - generic [ref=e13]: 密码
        - textbox "密码" [ref=e14]:
          - /placeholder: ••••••••
      - button "登录" [ref=e15] [cursor=pointer]
    - paragraph [ref=e17]:
      - text: 还没有账号？
      - link "立即注册" [ref=e18] [cursor=pointer]:
        - /url: /register
  - alert [ref=e19]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('每日推送 - 外部链接跳转', () => {
  4  |   const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
  5  |   const USERNAME = process.env.USERNAME || 'admin';
  6  |   const PASSWORD = process.env.PASSWORD || 'password';
  7  | 
  8  |   test.beforeEach(async ({ page }) => {
  9  |     await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
> 10 |     await page.getByLabel('用户名').fill(USERNAME);
     |                                  ^ Error: locator.fill: Test timeout of 30000ms exceeded.
  11 |     await page.getByLabel('密码').fill(PASSWORD);
  12 |     await page.getByRole('button', { name: '登录' }).click();
  13 |     await expect(page).toHaveURL(`${BASE_URL}/daily-push`, { timeout: 10000 });
  14 |     // 确保页面有外部链接文章，为简化，假设第一篇文章是外部链接
  15 |   });
  16 | 
  17 |   test('验证点击外部链接文章在新标签页打开', async ({ page, context }) => {
  18 |     // 准备监听新标签页
  19 |     const pagePromise = context.waitForEvent('page');
  20 |     // 点击外部链接文章卡片（假设卡片上有indicator标识外部链接，或直接点击所有卡片中带特定属性的）
  21 |     // 这里假设第一个是外部链接，实际需要根据data-testid区分
  22 |     await page.getByTestId('article-card').first().click();
  23 |     // 等待新标签页出现
  24 |     const newPage = await pagePromise;
  25 |     await newPage.waitForLoadState('domcontentloaded');
  26 |     // 新标签页URL应为外部链接
  27 |     const newUrl = newPage.url();
  28 |     expect(newUrl).not.toContain(BASE_URL);
  29 |   });
  30 | });
```