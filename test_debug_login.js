// 调试 localhost:3001 登录流程，排查 waitForURL 超时原因
const { chromium } = require('playwright');

const LOGIN_URL = 'http://localhost:3001/login';
const DASHBOARD_URL = 'http://localhost:3001/dashboard';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  console.log('1. 访问登录页:', LOGIN_URL);
  await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);
  console.log('   当前URL:', page.url());

  // 检查页面上的表单元素
  console.log('\n2. 检查页面元素:');
  const emailInput = page.getByRole('textbox', { name: '邮箱' });
  const pwdInput = page.getByRole('textbox', { name: '密码' });
  const loginBtn = page.getByRole('button', { name: '登录' });

  console.log('   邮箱输入框存在:', await emailInput.count());
  console.log('   密码输入框存在:', await pwdInput.count());
  console.log('   登录按钮存在:', await loginBtn.count());

  // 检查所有 textbox 和 button（帮助诊断）
  const allTextboxes = await page.getByRole('textbox').all();
  console.log('   页面所有 textbox 数量:', allTextboxes.length);
  for (let i = 0; i < allTextboxes.length; i++) {
    const label = await allTextboxes[i].getAttribute('aria-label');
    const placeholder = await allTextboxes[i].getAttribute('placeholder');
    const name = await allTextboxes[i].getAttribute('name');
    const type = await allTextboxes[i].getAttribute('type');
    console.log(`     [${i}] label=${label}, placeholder=${placeholder}, name=${name}, type=${type}`);
  }

  const allButtons = await page.getByRole('button').all();
  console.log('   页面所有 button 数量:', allButtons.length);
  for (let i = 0; i < allButtons.length; i++) {
    const text = (await allButtons[i].textContent()).trim();
    console.log(`     [${i}] text="${text}"`);
  }

  // 3. 填入凭证并点击登录
  console.log('\n3. 填入凭证并登录');
  // 先查看 profile 里的账号密码 —— 用默认测试值
  const username = 'admin@test.com';
  const password = 'pwd123';

  await emailInput.fill(username);
  await pwdInput.fill(password);
  console.log('   已填入账号密码');

  // 监听 URL 变化和导航事件
  page.on('framenavigated', frame => {
    if (frame === page.mainFrame()) {
      console.log('   [导航事件] URL 变为:', frame.url());
    }
  });

  await loginBtn.click();
  console.log('   已点击登录按钮');

  // 4. 等待并观察 URL 变化
  console.log('\n4. 等待 URL 变化（最多 15 秒）...');
  let finalUrl = page.url();
  for (let i = 0; i < 15; i++) {
    await page.waitForTimeout(1000);
    const currentUrl = page.url();
    if (currentUrl !== finalUrl) {
      console.log(`   [${i+1}s] URL 变化: ${finalUrl} -> ${currentUrl}`);
      finalUrl = currentUrl;
    }
  }
  console.log('   最终 URL:', finalUrl);

  // 5. 检查页面内容（是否登录成功或显示错误）
  console.log('\n5. 检查页面内容:');
  const bodyText = await page.locator('body').textContent();
  console.log('   页面文本前 200 字:', bodyText.replace(/\s+/g, ' ').trim().substring(0, 200));

  // 6. 测试不同的 waitForURL 模式
  console.log('\n6. 测试 waitForURL 匹配模式:');
  console.log('   当前 URL:', page.url());
  console.log('   目标 URL:', DASHBOARD_URL);

  // 测试 glob 模式
  const globPattern1 = `**${DASHBOARD_URL}**`;
  console.log(`   glob 模式1: ${globPattern1}`);

  // 检查页面是否有错误提示
  const errorElements = await page.locator('[role="alert"], .error, .error-message, .ant-message-error').count();
  console.log('   错误提示元素数量:', errorElements);

  await page.screenshot({ path: 'e:\\hkx_project\\TestPilot\\test_snapshot\\debug_login_result.png' });
  console.log('\n截图已保存: test_snapshot/debug_login_result.png');

  await browser.close();
  console.log('调试完成');
})();
