import { test, expect } from '@playwright/test';

test('生成登录会话快照', async ({ page }) => {
  // 1. 访问登录页
  await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });

  // 2. 填入凭证
  await (page.getByRole('textbox', { name: '邮箱' })).fill('huangkx1225@163.com');
  await (page.getByRole('textbox', { name: '密码' })).fill('123456');

  // 3. 点击提交
  await (page.getByRole('button', { name: '登录' })).click();

  // 4. 等待登录成功
  await page.waitForURL('**http://localhost:3001/dashboard**', { timeout: 10000 });

  // 5. 保存会话快照
  await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/2/profile-8.json' });
});
