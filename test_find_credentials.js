// 检查 localhost:3001 注册页面，查找可用账号
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  // 1. 尝试注册一个测试账号
  console.log('1. 尝试注册测试账号...');
  await page.goto('http://localhost:3001/register', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);
  console.log('   注册页 URL:', page.url());

  // 检查注册页元素
  const regInputs = await page.getByRole('textbox').all();
  console.log('   注册页 textbox 数量:', regInputs.length);
  for (let i = 0; i < regInputs.length; i++) {
    const placeholder = await regInputs[i].getAttribute('placeholder');
    const type = await regInputs[i].getAttribute('type');
    const ariaLabel = await regInputs[i].getAttribute('aria-label');
    console.log(`     [${i}] placeholder=${placeholder}, type=${type}, aria-label=${ariaLabel}`);
  }

  // 检查注册页是否有标签文字
  const bodyText = await page.locator('body').textContent();
  console.log('   注册页文本:', bodyText.replace(/\s+/g, ' ').trim().substring(0, 300));

  // 尝试注册
  if (regInputs.length >= 3) {
    console.log('\n2. 尝试注册...');
    try {
      // 尝试找到邮箱、密码、确认密码输入框
      const emailField = page.getByRole('textbox', { name: '邮箱' });
      const pwdField = page.getByRole('textbox', { name: '密码' });
      const confirmField = page.getByRole('textbox', { name: '确认密码' });

      if (await emailField.count() > 0 && await pwdField.count() > 0) {
        await emailField.fill('test@kaogong.com');
        await pwdField.fill('Test1234!');
        if (await confirmField.count() > 0) {
          await confirmField.fill('Test1234!');
        }
        const regBtn = page.getByRole('button', { name: '注册' });
        if (await regBtn.count() > 0) {
          await regBtn.click();
          await page.waitForTimeout(3000);
          console.log('   注册后 URL:', page.url());
          const afterText = await page.locator('body').textContent();
          console.log('   注册后文本:', afterText.replace(/\s+/g, ' ').trim().substring(0, 200));
        }
      }
    } catch (e) {
      console.log('   注册异常:', e.message);
    }
  }

  // 3. 尝试登录
  console.log('\n3. 尝试用注册的账号登录...');
  await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  const testAccounts = [
    { email: 'test@kaogong.com', pwd: 'Test1234!' },
    { email: 'admin@kaogong.com', pwd: 'admin123' },
    { email: 'test@example.com', pwd: 'test123' },
    { email: 'admin@test.com', pwd: 'Admin123!' },
  ];

  for (const acc of testAccounts) {
    console.log(`\n   尝试: ${acc.email} / ${acc.pwd}`);
    await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);

    await page.getByRole('textbox', { name: '邮箱' }).fill(acc.email);
    await page.getByRole('textbox', { name: '密码' }).fill(acc.pwd);
    await page.getByRole('button', { name: '登录' }).click();
    await page.waitForTimeout(2000);

    const currentUrl = page.url();
    console.log(`   登录后 URL: ${currentUrl}`);

    if (currentUrl.includes('dashboard')) {
      console.log('   ✓ 登录成功！');
      await page.screenshot({ path: 'e:\\hkx_project\\TestPilot\\test_snapshot\\debug_login_success.png' });
      console.log(`   成功凭证: email=${acc.email}, pwd=${acc.pwd}`);
      break;
    } else {
      const text = await page.locator('body').textContent();
      const errMatch = text.match(/(邮箱或密码错误|密码错误|用户不存在|登录失败[：:]?[^\s]*)/);
      console.log('   登录失败:', errMatch ? errMatch[0] : '未知原因');
    }
  }

  await browser.close();
  console.log('\n调试完成');
})();
