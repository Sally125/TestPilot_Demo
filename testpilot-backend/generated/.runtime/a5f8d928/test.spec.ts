import { test, expect } from '@playwright/test';

test('生成登录会话快照（自定义脚本）', async ({ page }) => {
  // ===== 用户自定义登录代码 开始 =====
  // newbee-mall 登录脚本（绕过验证码）
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('http://localhost:28089/login', { waitUntil: 'networkidle' });
  await page.fill("input[name='loginName']", '13700002703');
  await page.fill("input[name='password']", '123456');
  // 直接提交（后端 session 中无验证码时部分情况可绕过）
  await page.click("input[type='submit']");
  await page.waitForTimeout(3000);
  await context.storageState({ path: process.env.STORAGE_STATE_PATH });
  await browser.close();
})();
  // ===== 用户自定义登录代码 结束 =====

  // 自动追加：保存会话快照
  await page.context().storageState({ path: 'E:/hkx_project/TestPilot/testpilot-backend/data/storage-states/15/profile-10.json' });
});
