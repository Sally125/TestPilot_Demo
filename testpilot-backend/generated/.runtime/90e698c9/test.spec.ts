import { test, expect } from '@playwright/test';

test('生成登录会话快照（自定义脚本）', async ({ page }) => {
  // ===== 用户自定义登录代码 开始 =====
  await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle' });

await page.getByRole('textbox', { name: '邮箱' }).fill('huangkx1225@163.com');
await page.getByRole('textbox', { name: '密码' }).fill('123456');

await page.getByRole('button', { name: '登录' }).click();

await page.waitForURL('**/dashboard**', { timeout: 15000 });
  // ===== 用户自定义登录代码 结束 =====

  // 自动追加：保存会话快照
  await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/1/profile-2.json' });
});
