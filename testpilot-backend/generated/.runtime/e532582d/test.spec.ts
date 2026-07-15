import { test, expect } from '@playwright/test';

test('生成登录会话快照（自定义脚本）', async ({ page }) => {
  // ===== 用户自定义登录代码 开始 =====
  // 自定义 Playwright 登录脚本
// 可用对象：page（Playwright Page）
// 系统会自动追加 storageState 保存逻辑，无需手动保存

await page.goto('http://localhost:3000/login');

await page.getByRole('邮箱').fill('huangkx1225@163.com');
await page.getByRole('密码').fill('123456');

await page.getByRole('button', { name: '登录' }).click();

// 等待登录成功（URL 变化或元素出现）
await page.waitForURL('**/dashboard**', { timeout: 15000 });
  // ===== 用户自定义登录代码 结束 =====

  // 自动追加：保存会话快照
  await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/1/profile-2.json' });
});
