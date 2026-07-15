// 诊断前端 UI 消失问题
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  const errors = [];
  const consoleMessages = [];

  page.on('console', msg => {
    consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
  });
  page.on('pageerror', err => {
    errors.push(`PAGE ERROR: ${err.message}\n${err.stack || ''}`);
  });
  page.on('requestfailed', req => {
    errors.push(`REQUEST FAILED: ${req.url()} - ${req.failure()?.errorText}`);
  });

  try {
    await page.goto('http://localhost:8080/AI%E6%B5%8B%E8%AF%95%E6%99%BA%E8%83%BD%E4%BD%93_TestPilot.html', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // 等待 5 秒让 JS 执行完
    await page.waitForTimeout(5000);

    // 检查侧边栏导航项
    const navItems = await page.$$eval('.nav-item', els => els.map(e => ({
      text: e.textContent?.trim(),
      display: window.getComputedStyle(e).display,
      visible: e.offsetParent !== null
    })));
    console.log('=== 侧边栏导航项 ===');
    console.log(JSON.stringify(navItems, null, 2));

    // 检查各个页面是否存在
    const pages = await page.$$eval('[id^="page-"]', els => els.map(e => ({
      id: e.id,
      display: window.getComputedStyle(e).display,
      childrenCount: e.children.length,
      innerHTML_length: e.innerHTML.length,
      innerHTML_preview: e.innerHTML.substring(0, 100)
    })));
    console.log('\n=== 页面区域 ===');
    console.log(JSON.stringify(pages, null, 2));

    // 检查项目列表
    const projectCount = await page.$$eval('#project-table-body tr, .project-item', els => els.length).catch(() => -1);
    console.log(`\n项目列表元素数: ${projectCount}`);

    // 检查 projectData 变量
    const projectDataInfo = await page.evaluate(() => {
      try {
        if (typeof projectData === 'undefined') return 'projectData undefined';
        if (!Array.isArray(projectData)) return `projectData not array: ${typeof projectData}`;
        return `projectData length: ${projectData.length}, currentProjectIdx: ${typeof currentProjectIdx !== 'undefined' ? currentProjectIdx : 'undefined'}`;
      } catch (e) {
        return `eval error: ${e.message}`;
      }
    });
    console.log(projectDataInfo);

    // 检查每个项目的数据
    const dataInfo = await page.evaluate(() => {
      try {
        if (typeof projectData === 'undefined') return null;
        return projectData.map((p, i) => ({
          idx: i,
          name: p.name,
          reqCount: p.requirements?.length || 0,
          caseCount: p.testcases?.cases?.length || 0,
          execCount: p.execution?.items?.length || 0,
          reportCount: p.reportList?.length || 0,
          dataLoaded: !!p._dataLoaded
        }));
      } catch (e) {
        return `error: ${e.message}`;
      }
    });
    console.log('\n=== 前端 projectData ===');
    console.log(JSON.stringify(dataInfo, null, 2));

    // 检查当前显示的页面
    const visiblePage = await page.evaluate(() => {
      const pages = document.querySelectorAll('[id^="page-"]');
      for (const p of pages) {
        if (window.getComputedStyle(p).display !== 'none') {
          return { id: p.id, childrenCount: p.children.length };
        }
      }
      return 'no visible page';
    });
    console.log('\n当前可见页面:', JSON.stringify(visiblePage));

  } catch (e) {
    console.log('导航错误:', e.message);
  }

  console.log('\n=== 页面错误 ===');
  if (errors.length === 0) console.log('无错误');
  else errors.forEach(e => console.log(e));

  console.log('\n=== 控制台消息（仅 error/warning）===');
  const filtered = consoleMessages.filter(m => m.includes('[error]') || m.includes('[warning]'));
  if (filtered.length === 0) console.log('无 error/warning 消息');
  else filtered.forEach(m => console.log(m));

  await page.screenshot({ path: 'e:/hkx_project/TestPilot/test_snapshot/diag_ui_missing.png', fullPage: true });
  console.log('\n截图已保存: diag_ui_missing.png');

  await browser.close();
})();
