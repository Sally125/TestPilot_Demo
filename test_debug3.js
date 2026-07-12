const { chromium } = require('playwright');
const HTML_PATH = 'e:\\hkx_project\\TestPilot\\AI测试智能体_TestPilot.html';
const URL = 'file:///' + HTML_PATH.replace(/\\/g, '/');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  page.on('console', msg => console.log('[PAGE]', msg.text()));

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.evaluate(() => selectProject(0));
  await page.waitForTimeout(500);

  // 手动设置 currentAnalysisResult,然后直接调用 handleGenerateTestcases
  console.log('===== 直接调用 handleGenerateTestcases =====');
  const result = await page.evaluate(async () => {
    currentAnalysisResult = {
      feature_points: [{
        name: '添加待办',
        priority: 'P0',
        test_dimensions: ['功能测试'],
        business_logic: '输入回车添加',
        risk_hint: '空输入'
      }],
      requirementId: null,
      estimated_case_count: 2
    };
    try {
      await handleGenerateTestcases();
      return 'OK';
    } catch (e) {
      return 'ERROR: ' + e.message;
    }
  });
  console.log('调用结果:', result);
  await page.waitForTimeout(15000);

  const cases = await page.evaluate(() => fetch('http://localhost:8000/api/projects/1/testcases').then(r => r.json()));
  console.log('后端用例数:', cases.length);

  await browser.close();
})();
