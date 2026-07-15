import { test, expect } from '@playwright/test';

test('生成登录会话快照', async ({ page }) => {
  // 1. 访问登录页（用 networkidle 确保 Next.js/React 完成 hydration，否则表单状态不生效）
  await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle' });

  // 2. 填入凭证（先等待元素可交互）
  await (page.locator('#email')).waitFor({ state: 'visible', timeout: 10000 });
  await (page.locator('#email')).fill('tester@kaogong.com');
  await (page.locator('#password')).fill('Test1234!');

  // 3. 点击提交
  await (page.locator('button[type=\'submit\']')).click();

  // 4. 等待登录成功
  await page.waitForURL('**/dashboard**', { timeout: 15000 });

  // 5. 保存会话快照
  await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/22/profile-15.json' });
});
