import { test, expect } from '@playwright/test';

test('生成登录会话快照（自定义脚本）', async ({ page }) => {
  // ===== 用户自定义登录代码 开始 =====
  // 登录脚本模板 - 请根据实际页面修改
await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });

// 填写凭证（请修改为实际的账号密码和选择器）
await page.getByPlaceholder('邮箱').fill('huangkx1225@163.com');
await page.getByPlaceholder('密码').fill('1223456');

// 点击登录按钮
await page.getByRole('button', { name: '登录' }).click();

// 等待登录成功（URL跳转或元素出现）
await page.waitForURL('**/dashboard**', { timeout: 10000 });
  // ===== 用户自定义登录代码 结束 =====

  // 自动追加：保存会话快照
  await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/2/profile-8.json' });
});
