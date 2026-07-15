import { test, expect } from '@playwright/test';

test('生成登录会话快照', async ({ page }) => {
  // 1. 访问登录页
  await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });

  // 2. 填入凭证
  await (page.getByPlaceholder(/用户名|邮箱|email|username/i)).fill('admin@test.com');
  await (page.getByPlaceholder(/密码|password/i)).fill('pwd123');

  // 3. 点击提交
  await (page.getByRole('button', { name: /登录|sign in|log in/i })).click();

  // 4. 等待登录成功
  await page.waitForLoadState('networkidle', { timeout: 10000 });

  // 5. 保存会话快照
  await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/1/profile-2.json' });
});
