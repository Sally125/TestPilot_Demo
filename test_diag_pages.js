// 专门诊断用例库和报告中心页面不渲染问题
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  const errors = [];
  page.on('pageerror', err => errors.push(`PAGE ERROR: ${err.message}`));
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(`[console.error] ${msg.text()}`);
  });

  await page.goto('http://localhost:8080/AI%E6%B5%8B%E8%AF%95%E6%99%BA%E8%83%BD%E4%BD%93_TestPilot.html', {
    waitUntil: 'networkidle',
    timeout: 30000
  });
  await page.waitForTimeout(5000);

  // 1. 检查所有 .page 元素
  const allPages = await page.$$eval('.page', els => els.map(e => ({
    id: e.id,
    className: e.className,
    display: window.getComputedStyle(e).display,
    childrenCount: e.children.length,
    innerHTMLLength: e.innerHTML.length,
    innerHTMLPreview: e.innerHTML.substring(0, 80)
  })));
  console.log('=== 所有 .page 元素 ===');
  allPages.forEach(p => console.log(JSON.stringify(p)));

  // 2. 检查 navItems 数量
  const navCount = await page.$$eval('.nav-item', els => els.length);
  console.log(`\nnav-item 数量: ${navCount}`);

  // 3. 检查 JS 变量 pages 和 navItems
  const jsInfo = await page.evaluate(() => {
    // 检查全局变量
    const info = {};
    try { info.currentPageId = typeof currentPageId !== 'undefined' ? currentPageId : 'undefined'; } catch(e) { info.currentPageId = 'err:' + e.message; }
    try { info.currentProjectIdx = typeof currentProjectIdx !== 'undefined' ? currentProjectIdx : 'undefined'; } catch(e) { info.currentProjectIdx = 'err:' + e.message; }
    try { info.projectDataLen = typeof projectData !== 'undefined' ? projectData.length : 'undefined'; } catch(e) { info.projectDataLen = 'err:' + e.message; }
    // 检查 page-testcases 的 DOM
    const tc = document.getElementById('page-testcases');
    info.pageTestcases = tc ? { exists: true, children: tc.children.length, innerHTMLLen: tc.innerHTML.length, display: window.getComputedStyle(tc).display } : { exists: false };
    const rp = document.getElementById('page-report');
    info.pageReport = rp ? { exists: true, children: rp.children.length, innerHTMLLen: rp.innerHTML.length, display: window.getComputedStyle(rp).display } : { exists: false };
    const ex = document.getElementById('page-execution');
    info.pageExecution = ex ? { exists: true, children: ex.children.length, innerHTMLLen: ex.innerHTML.length, display: window.getComputedStyle(ex).display } : { exists: false };
    return info;
  });
  console.log('\n=== JS 状态 ===');
  console.log(JSON.stringify(jsInfo, null, 2));

  // 4. 尝试手动调用 switchPage('testcases') 看是否报错
  console.log('\n=== 尝试 switchPage("testcases") ===');
  const switchResult = await page.evaluate(() => {
    try {
      switchPage('testcases');
      return 'switchPage 调用成功';
    } catch(e) {
      return `switchPage 错误: ${e.message}\n${e.stack}`;
    }
  });
  console.log(switchResult);
  await page.waitForTimeout(2000);

  // 检查调用后的状态
  const afterSwitch = await page.evaluate(() => {
    const tc = document.getElementById('page-testcases');
    return {
      display: window.getComputedStyle(tc).display,
      children: tc.children.length,
      innerHTMLLen: tc.innerHTML.length,
      innerHTMLPreview: tc.innerHTML.substring(0, 200)
    };
  });
  console.log('切换后 page-testcases:', JSON.stringify(afterSwitch, null, 2));

  // 5. 尝试手动调用 refreshProjectContent
  console.log('\n=== 尝试 refreshProjectContent() ===');
  const refreshResult = await page.evaluate(() => {
    try {
      refreshProjectContent();
      return 'refreshProjectContent 调用成功';
    } catch(e) {
      return `refreshProjectContent 错误: ${e.message}\n${e.stack}`;
    }
  });
  console.log(refreshResult);
  await page.waitForTimeout(1000);

  const afterRefresh = await page.evaluate(() => {
    const tc = document.getElementById('page-testcases');
    const rp = document.getElementById('page-report');
    const ex = document.getElementById('page-execution');
    return {
      testcases: { children: tc.children.length, innerHTMLLen: tc.innerHTML.length },
      report: { children: rp.children.length, innerHTMLLen: rp.innerHTML.length },
      execution: { children: ex.children.length, innerHTMLLen: ex.innerHTML.length }
    };
  });
  console.log('refreshProjectContent 后:', JSON.stringify(afterRefresh, null, 2));

  // 6. 检查 renderTestcases 函数是否能执行
  console.log('\n=== 尝试直接调用 renderTestcases ===');
  const renderResult = await page.evaluate(() => {
    try {
      const data = projectData[currentProjectIdx];
      const html = renderTestcases(data);
      return { success: true, htmlLength: html.length, htmlPreview: html.substring(0, 200) };
    } catch(e) {
      return { success: false, error: e.message, stack: e.stack };
    }
  });
  console.log(JSON.stringify(renderResult, null, 2));

  console.log('\n=== 页面错误汇总 ===');
  if (errors.length === 0) console.log('无错误');
  else errors.forEach(e => console.log(e));

  await page.screenshot({ path: 'e:/hkx_project/TestPilot/test_snapshot/diag_pages.png', fullPage: true });
  console.log('\n截图已保存');

  await browser.close();
})();
