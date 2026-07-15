// 端到端测试：使用正确凭证和选择器，调用后端 API 生成会话
const { chromium } = require('playwright');
const http = require('http');

const API = 'localhost:8000';
const PROJECT_ID = 3; // 考公大师v2

function apiRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = http.request({
      hostname: API.split(':')[0],
      port: API.split(':')[1],
      path: '/api' + path,
      method: method,
      headers: data ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } : {}
    }, (res) => {
      let chunks = '';
      res.on('data', c => chunks += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(chunks) }); }
        catch (e) { resolve({ status: res.statusCode, data: chunks }); }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

(async () => {
  console.log('=== 端到端测试：生成登录会话 ===\n');

  // 步骤 1：先在浏览器里验证登录流程（用 Playwright 模拟后端生成的脚本）
  console.log('步骤 1：浏览器验证登录流程');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // 模拟后端生成的脚本逻辑
  console.log('  访问登录页:', page.url());

  // 用 locator 类型选择器
  await page.getByRole('textbox', { name: '邮箱' }).fill('tester@kaogong.com');
  await page.getByRole('textbox', { name: '密码' }).fill('Test1234!');
  console.log('  已填入凭证');

  await page.getByRole('button', { name: '登录' }).click();
  console.log('  已点击登录');

  // 测试 waitForURL —— 模拟后端生成的代码
  try {
    await page.waitForURL('http://localhost:3001/dashboard**', { timeout: 15000 });
    console.log('  ✓ waitForURL 成功！当前 URL:', page.url());
  } catch (e) {
    console.log('  ✗ waitForURL 失败:', e.message.substring(0, 80));
    console.log('  当前 URL:', page.url());
    const text = await page.locator('body').textContent();
    console.log('  页面文本:', text.replace(/\s+/g, ' ').trim().substring(0, 150));
  }

  await page.screenshot({ path: 'e:\\hkx_project\\TestPilot\\test_snapshot\\e2e_browser_login.png' });
  await browser.close();

  // 步骤 2：通过 API 创建/更新 profile（表单模式 + locator 选择器）
  console.log('\n步骤 2：配置登录态 profile（表单模式 + locator）');

  // 先查看现有 profiles
  const profilesResp = await apiRequest('GET', `/projects/${PROJECT_ID}/login-profiles`);
  console.log('  现有 profiles:', profilesResp.data.map(p => ({ id: p.id, name: p.name, mode: p.scriptMode })));

  // 找到非 anonymous 的 profile 或创建新的
  let profile = profilesResp.data.find(p => p.id !== 'anonymous');
  let profileId;

  const profileConfig = {
    name: '考公大师管理员',
    role: 'admin',
    username: 'tester@kaogong.com',
    password: 'Test1234!',
    loginUrl: 'http://localhost:3001/login',
    scriptMode: 'form',
    // locator 类型的选择器
    usernameSelector: "getByRole('textbox', { name: '邮箱' })",
    usernameSelectorType: 'locator',
    passwordSelector: "getByRole('textbox', { name: '密码' })",
    passwordSelectorType: 'locator',
    submitSelector: "getByRole('button', { name: '登录' })",
    submitSelectorType: 'locator',
    // URL 类型成功标志
    successIndicator: 'http://localhost:3001/dashboard',
    successIndicatorType: 'url',
  };

  if (profile) {
    // 更新现有
    profileId = profile.id;
    console.log(`  更新 profile #${profileId}...`);
    const updateResp = await apiRequest('PUT', `/login-profiles/${profileId}`, profileConfig);
    console.log('  更新结果:', updateResp.status, updateResp.data.scriptMode, updateResp.data.usernameSelectorType);
  } else {
    // 创建新的
    console.log('  创建新 profile...');
    const createResp = await apiRequest('POST', `/projects/${PROJECT_ID}/login-profiles`, profileConfig);
    console.log('  创建结果:', createResp.status, createResp.data.id);
    profileId = createResp.data.id;
  }

  // 步骤 3：调用生成会话 API
  console.log(`\n步骤 3：调用生成会话 API（profile #${profileId}）`);
  console.log('  等待中...（最多 90 秒）');

  const genResp = await apiRequest('POST', `/login-profiles/${profileId}/generate-session`, {});
  console.log('  生成结果状态:', genResp.status);

  if (genResp.data.success) {
    console.log('  ✓ 会话生成成功！');
    console.log('  storageStatePath:', genResp.data.storageStatePath);
    console.log('  耗时:', genResp.data.duration_ms, 'ms');
    console.log('  截图数:', genResp.data.screenshots?.length || 0);
  } else {
    console.log('  ✗ 会话生成失败');
    console.log('  错误:', genResp.data.error);
    console.log('  stdout:', (genResp.data.stdout || '').substring(0, 300));
    console.log('  stderr:', (genResp.data.stderr || '').substring(0, 300));
  }

  console.log('\n=== 测试完成 ===');
})();
