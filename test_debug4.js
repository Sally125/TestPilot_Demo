const { chromium } = require('playwright');
const HTML_PATH = 'e:\\hkx_project\\TestPilot\\AI测试智能体_TestPilot.html';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  page.on('console', msg => console.log('[PAGE]', msg.text()));
  page.on('pageerror', err => console.log('[JS]', String(err)));

  await page.goto('file:///' + HTML_PATH.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.evaluate(() => selectProject(0));
  await page.waitForTimeout(500);

  // 设置假的 analysisResult,直接切到 analysis 页,测试按钮
  await page.evaluate(() => {
    currentAnalysisResult = {
      feature_points: [{ name: '测试', priority: 'P0', test_dimensions: ['功能'], business_logic: '逻辑', risk_hint: '' }],
      estimated_case_count: 2
    };
    updateAnalysisPage(currentAnalysisResult);
  });
  await page.evaluate(() => switchPage('analysis'));
  await page.waitForTimeout(500);

  // 检查按钮
  const btnInfo = await page.evaluate(() => {
    const btns = document.querySelectorAll('#page-analysis button');
    return Array.from(btns).map(b => ({ text: b.textContent.trim(), html: b.outerHTML.slice(0,100) }));
  });
  console.log('analysis 页按钮:', JSON.stringify(btnInfo, null, 2));

  // 点击"确认并生成用例"
  console.log('点击按钮...');
  await page.locator('#page-analysis button:has-text("确认并生成用例")').click();
  await page.waitForTimeout(3000);

  const p = await page.locator('.page.active').getAttribute('id');
  console.log('点击后页:', p);

  await browser.close();
})();
