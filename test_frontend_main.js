// TestPilot 主要功能前端 E2E 测试
// 覆盖：页面加载、侧边栏导航、各功能页面渲染、执行中心、生成会话弹窗
const { chromium } = require('playwright');

const URL = 'http://localhost:8080/AI%E6%B5%8B%E8%AF%95%E6%99%BA%E8%83%BD%E4%BD%93_TestPilot.html';
const SHOT = 'e:\\hkx_project\\TestPilot\\test_snapshot';
const results = [];
const errors = [];

function record(name, ok, detail) {
  results.push({ name, ok, detail });
  console.log(`  ${ok ? '✓' : '✗'} ${name.padEnd(24)} ${detail}`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(e.message));

  const log = (m) => console.log(`[${new Date().toLocaleTimeString()}] ${m}`);

  try {
    // ========== 1. 页面加载 ==========
    log('1. 页面加载测试');
    await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);

    const title = await page.title();
    record('页面加载', title.length > 0, `title="${title.substring(0, 30)}"`);

    // 检查侧边栏导航项
    const navItems = await page.locator('.nav-item').count();
    record('侧边栏导航', navItems >= 5, `${navItems} 个导航项`);

    await page.screenshot({ path: `${SHOT}\\main_01_home.png` });

    // ========== 2. 仪表盘页面 ==========
    log('2. 仪表盘页面');
    await page.locator('[data-page="dashboard"]').first().click();
    await page.waitForTimeout(1500);
    const dashVisible = await page.locator('#page-dashboard').isVisible().catch(() => false);
    const statsCards = await page.locator('#page-dashboard .stat-card, #page-dashboard .dashboard-card, #page-dashboard .card').count();
    record('仪表盘渲染', dashVisible, `${statsCards} 个统计卡片`);
    await page.screenshot({ path: `${SHOT}\\main_02_dashboard.png` });

    // ========== 3. 项目管理页面 ==========
    log('3. 项目管理页面');
    await page.locator('[data-page="projects"]').first().click();
    await page.waitForTimeout(1500);
    const projVisible = await page.locator('#page-projects').isVisible().catch(() => false);
    const projCards = await page.locator('#page-projects .project-card, #page-projects .card').count();
    record('项目管理渲染', projVisible, `${projCards} 个项目卡片`);
    await page.screenshot({ path: `${SHOT}\\main_03_projects.png` });

    // ========== 4. 需求管理页面 ==========
    log('4. 需求管理页面');
    await page.locator('[data-page="requirement"]').first().click();
    await page.waitForTimeout(1500);
    const reqVisible = await page.locator('#page-requirement').isVisible().catch(() => false);
    record('需求管理渲染', reqVisible, reqVisible ? '页面可见' : '页面不可见');
    await page.screenshot({ path: `${SHOT}\\main_04_requirement.png` });

    // ========== 5. 用例库页面 ==========
    log('5. 用例库页面');
    await page.locator('[data-page="testcases"]').first().click();
    await page.waitForTimeout(1500);
    const tcVisible = await page.locator('#page-testcases').isVisible().catch(() => false);
    const tcRows = await page.locator('#page-testcases .case-row, #page-testcases .testcase-item, #page-testcases tbody tr').count();
    record('用例库渲染', tcVisible, `${tcRows} 条用例`);
    await page.screenshot({ path: `${SHOT}\\main_05_testcases.png` });

    // ========== 6. 报告中心页面 ==========
    log('6. 报告中心页面');
    await page.locator('[data-page="report"]').first().click();
    await page.waitForTimeout(1500);
    const repVisible = await page.locator('#page-report').isVisible().catch(() => false);
    record('报告中心渲染', repVisible, repVisible ? '页面可见' : '页面不可见');
    await page.screenshot({ path: `${SHOT}\\main_06_report.png` });

    // ========== 7. 设置页面 ==========
    log('7. 设置页面');
    await page.locator('[data-page="settings"]').first().click();
    await page.waitForTimeout(1500);
    const setVisible = await page.locator('#page-settings').isVisible().catch(() => false);
    record('设置页面渲染', setVisible, setVisible ? '页面可见' : '页面不可见');
    await page.screenshot({ path: `${SHOT}\\main_07_settings.png` });

    // ========== 8. 执行中心（模态框） ==========
    log('8. 执行中心模态框');
    await page.evaluate(() => openExecutionModal());
    await page.waitForTimeout(1500);
    const execModal = await page.locator('#execution-modal.show').count();
    const execBody = await page.locator('#execution-modal-body').innerHTML().catch(() => '');
    record('执行中心打开', execModal > 0, `body长度=${execBody.length}`);
    await page.screenshot({ path: `${SHOT}\\main_08_exec_center.png` });

    // ========== 9. 登录态配置面板 ==========
    log('9. 登录态配置面板');
    await page.evaluate(() => showLoginConfig());
    await page.waitForTimeout(1500);
    const loginConfigVisible = await page.locator('#login-profiles-modal, [id*="login-profile"], [class*="login-config"]').first().isVisible().catch(() => false);
    // 检查是否有登录态卡片
    const profileCards = await page.locator('text=测试管理员, text=管理员, text=匿名').count();
    record('登录态配置面板', loginConfigVisible || profileCards > 0, `${profileCards} 个匹配`);
    await page.screenshot({ path: `${SHOT}\\main_09_login_profiles.png` });

    // ========== 10. 生成会话弹窗（脚本模式切换） ==========
    log('10. 生成会话弹窗');
    // 关闭可能存在的登录态弹窗，重新打开执行中心
    await page.evaluate(() => {
      const m = document.getElementById('login-profiles-modal');
      if (m) m.remove();
      // 找到第一个可用的 profile id
      const profiles = (typeof loginProfilesCache !== 'undefined' && loginProfilesCache) ? loginProfilesCache : [];
      const p = profiles.find(x => x.id && x.id !== 'anonymous');
      if (p) showGenerateSessionGuide(p.id);
    });
    await page.waitForTimeout(1000);

    const genModal = await page.locator('#generate-session-modal').count();
    if (genModal > 0) {
      record('生成会话弹窗打开', true, '弹窗可见');

      // 验证模式切换按钮存在
      const hasFormBtn = await page.locator('#gs-mode-form-btn').count();
      const hasCustomBtn = await page.locator('#gs-mode-custom-btn').count();
      record('模式切换按钮', hasFormBtn > 0 && hasCustomBtn > 0, `form=${hasFormBtn} custom=${hasCustomBtn}`);

      // 切换到脚本模式
      await page.locator('#gs-mode-custom-btn').click();
      await page.waitForTimeout(500);
      const customDivVisible = await page.locator('#gs-custom-mode').isVisible();
      record('切换到脚本模式', customDivVisible, customDivVisible ? '脚本区可见' : '脚本区不可见');

      // 插入模板
      const insertBtn = await page.locator('button:has-text("插入模板")').count();
      if (insertBtn > 0) {
        await page.locator('button:has-text("插入模板")').first().click();
        await page.waitForTimeout(300);
        const scriptLen = (await page.locator('#gs-custom-script').inputValue()).length;
        record('插入模板', scriptLen > 0, `脚本长度=${scriptLen}`);
      } else {
        record('插入模板', false, '未找到按钮');
      }

      await page.screenshot({ path: `${SHOT}\\main_10_gen_session.png` });

      // 关闭弹窗
      await page.evaluate(() => {
        const m = document.getElementById('generate-session-modal');
        if (m) m.remove();
      });
    } else {
      record('生成会话弹窗打开', false, '弹窗未打开');
    }

    // ========== 11. 项目切换功能 ==========
    log('11. 项目切换功能');
    await page.evaluate(() => closeExecutionModal && closeExecutionModal());
    await page.waitForTimeout(500);
    await page.locator('[data-page="projects"]').first().click();
    await page.waitForTimeout(1000);
    const projSwitchWorks = await page.evaluate(() => {
      // 检查全局变量
      return typeof currentProjectIdx !== 'undefined' && typeof projectData !== 'undefined' && projectData.length > 0;
    });
    record('项目切换数据加载', projSwitchWorks, projSwitchWorks ? '全局数据已加载' : '数据未加载');
    await page.screenshot({ path: `${SHOT}\\main_11_project_switch.png` });

    // ========== 12. API 连通性（前端调用后端） ==========
    log('12. 前后端 API 连通性');
    const apiOk = await page.evaluate(async () => {
      try {
        const r = await fetch('/api/projects');
        return r.ok;
      } catch (e) {
        return false;
      }
    });
    record('前后端 API 连通', apiOk, apiOk ? '/api/projects 可访问' : '连接失败');

  } catch (e) {
    record('测试执行', false, '异常: ' + e.message);
    await page.screenshot({ path: `${SHOT}\\main_error.png` }).catch(() => {});
  }

  // 输出汇总
  console.log('\n' + '='.repeat(70));
  console.log('TestPilot 主要功能前端 E2E 测试结果');
  console.log('='.repeat(70));
  const passed = results.filter(r => r.ok).length;
  const failed = results.length - passed;
  for (const r of results) {
    const mark = r.ok ? '✓' : '✗';
    console.log(`  ${mark} ${r.name.padEnd(24)} ${r.detail}`);
  }
  console.log('-'.repeat(70));
  console.log(`  通过 ${passed}/${results.length}，失败 ${failed}`);
  if (errors.length > 0) {
    console.log(`\n  Console 错误 (${errors.length} 条):`);
    errors.slice(0, 5).forEach(e => console.log('    - ' + e.substring(0, 100)));
  } else {
    console.log('  无 Console 错误');
  }
  console.log('='.repeat(70));

  await browser.close();
})();
