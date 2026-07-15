// 精确对比：用 Playwright test runner（和后端相同方式）运行登录脚本
const { chromium } = require('playwright');

(async () => {
  console.log('=== 精确诊断：Playwright test runner 登录失败 ===\n');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  // 监听所有请求和响应
  const requests = [];
  page.on('response', async (resp) => {
    if (resp.url().includes('/api/') || resp.url().includes('login') || resp.url().includes('auth')) {
      let body = '';
      try { body = (await resp.text()).substring(0, 200); } catch(e) {}
      requests.push({ url: resp.url(), status: resp.status(), body });
    }
  });

  // 1. 访问登录页
  console.log('1. 访问登录页');
  await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });
  console.log('   URL:', page.url());

  // 等待 hydration 完成（Next.js 需要）
  console.log('   等待 hydration...');
  await page.waitForTimeout(2000);

  // 2. 检查输入框是否可交互
  console.log('\n2. 检查输入框状态');
  const emailBox = page.getByRole('textbox', { name: '邮箱' });
  const pwdBox = page.getByRole('textbox', { name: '密码' });
  const loginBtn = page.getByRole('button', { name: '登录' });

  const emailVisible = await emailBox.isVisible();
  const emailEnabled = await emailBox.isEnabled();
  const pwdVisible = await pwdBox.isVisible();
  const pwdEnabled = await pwdBox.isEnabled();
  console.log(`   邮箱框: visible=${emailVisible}, enabled=${emailEnabled}`);
  console.log(`   密码框: visible=${pwdVisible}, enabled=${pwdEnabled}`);

  // 3. 填入凭证
  console.log('\n3. 填入凭证');
  await emailBox.fill('tester@kaogong.com');
  await pwdBox.fill('Test1234!');
  console.log('   邮箱值:', await emailBox.inputValue());
  console.log('   密码值:', await pwdBox.inputValue());

  // 4. 点击登录并监听
  console.log('\n4. 点击登录');
  await loginBtn.click();

  // 等待响应
  await page.waitForTimeout(5000);

  console.log('\n5. 网络请求记录:');
  requests.forEach((r, i) => {
    console.log(`   [${i}] ${r.status} ${r.url}`);
    if (r.body) console.log(`       body: ${r.body.substring(0, 150)}`);
  });

  console.log('\n6. 最终状态:');
  console.log('   URL:', page.url());
  const text = await page.locator('body').textContent();
  console.log('   页面文本:', text.replace(/\s+/g, ' ').trim().substring(0, 250));

  // 检查 alert 内容
  const alertEl = page.locator('[role="alert"]');
  if (await alertEl.count() > 0) {
    const alertText = await alertEl.textContent();
    console.log('   Alert 内容:', alertText.trim());
  }

  await page.screenshot({ path: 'e:\\hkx_project\\TestPilot\\test_snapshot\\e2e_diag_result.png' });

  // 7. 关键测试：用 networkidle 等待
  console.log('\n7. 重新尝试：用 networkidle 等待 hydration');
  await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  await page.getByRole('textbox', { name: '邮箱' }).fill('tester@kaogong.com');
  await page.getByRole('textbox', { name: '密码' }).fill('Test1234!');
  await page.getByRole('button', { name: '登录' }).click();

  try {
    await page.waitForURL('http://localhost:3001/dashboard**', { timeout: 15000 });
    console.log('   ✓ networkidle 模式登录成功！URL:', page.url());
  } catch (e) {
    console.log('   ✗ 仍然失败');
    console.log('   URL:', page.url());
    const alertText2 = await page.locator('[role="alert"]').textContent().catch(() => '无alert');
    console.log('   Alert:', alertText2.trim());
  }

  await browser.close();
  console.log('\n=== 诊断完成 ===');
})();
