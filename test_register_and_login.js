// 注册测试账号并验证登录流程
const { chromium } = require('playwright');

const TEST_EMAIL = 'tester@kaogong.com';
const TEST_PWD = 'Test1234!';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  // 1. 注册账号
  console.log('1. 注册测试账号...');
  await page.goto('http://localhost:3001/register', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);

  // 注册页有4个输入框: 姓名、邮箱、密码、确认密码
  await page.getByPlaceholder('你的名字').fill('测试员');
  await page.getByPlaceholder('your@email.com').fill(TEST_EMAIL);
  await page.getByPlaceholder('至少6位').fill(TEST_PWD);
  await page.getByPlaceholder('再次输入密码').fill(TEST_PWD);

  console.log('   已填入注册信息');

  // 点击注册按钮
  await page.getByRole('button', { name: '注册' }).click();
  await page.waitForTimeout(3000);

  const afterRegUrl = page.url();
  console.log('   注册后 URL:', afterRegUrl);
  const afterRegText = await page.locator('body').textContent();
  console.log('   注册后文本:', afterRegText.replace(/\s+/g, ' ').trim().substring(0, 200));

  // 2. 用注册的账号登录
  console.log('\n2. 用注册账号登录...');
  await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  console.log('   登录页 URL:', page.url());

  // 用用户提供的 locator 登录
  await page.getByRole('textbox', { name: '邮箱' }).fill(TEST_EMAIL);
  await page.getByRole('textbox', { name: '密码' }).fill(TEST_PWD);
  console.log('   已填入账号密码');

  await page.getByRole('button', { name: '登录' }).click();
  console.log('   已点击登录按钮');

  // 等待 URL 变化
  await page.waitForTimeout(3000);
  const afterLoginUrl = page.url();
  console.log('   登录后 URL:', afterLoginUrl);

  if (afterLoginUrl.includes('dashboard')) {
    console.log('   ✓ 登录成功！URL 已跳转到 dashboard');
    await page.screenshot({ path: 'e:\\hkx_project\\TestPilot\\test_snapshot\\debug_login_success.png' });

    // 3. 测试 waitForURL 的不同 glob 模式
    console.log('\n3. 测试 waitForURL glob 模式匹配:');
    const targetUrl = 'http://localhost:3001/dashboard';

    // 测试模式1: **url** (当前代码生成的)
    const pattern1 = `**${targetUrl}**`;
    // 测试模式2: 直接 URL (无 glob)
    const pattern2 = targetUrl;
    // 测试模式3: **/path (只匹配路径)
    const pattern3 = '**/dashboard';
    // 测试模式4: url** (前缀匹配)
    const pattern4 = `${targetUrl}**`;

    console.log(`   当前 URL: ${afterLoginUrl}`);
    console.log(`   模式1 (${pattern1}): ${afterLoginUrl.includes(targetUrl) ? '应该匹配' : '不匹配'}`);
    console.log(`   模式2 (${pattern2}): 精确匹配 = ${afterLoginUrl === targetUrl}`);
    console.log(`   模式3 (${pattern3}): 路径匹配 = ${afterLoginUrl.includes('/dashboard')}`);
    console.log(`   模式4 (${pattern4}): 前缀匹配 = ${afterLoginUrl.startsWith(targetUrl)}`);

    // 实际 URL 可能是 /dashboard/tasks 等
    console.log(`\n   实际 URL: ${afterLoginUrl}`);
    console.log(`   注意: 实际跳转可能是 /dashboard/tasks 而非 /dashboard`);

  } else {
    console.log('   ✗ 登录失败');
    const text = await page.locator('body').textContent();
    console.log('   页面文本:', text.replace(/\s+/g, ' ').trim().substring(0, 200));
  }

  await browser.close();
  console.log('\n调试完成');
})();
