const { chromium } = require('playwright');
const HTML_PATH = 'e:\\hkx_project\\TestPilot\\AI测试智能体_TestPilot.html';
const URL = 'file:///' + HTML_PATH.replace(/\\/g, '/');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  page.on('console', msg => {
    const t = msg.text();
    if (t.includes('[') || t.includes('持久化') || t.includes('Generate') || t.includes('Analysis') || t.includes('error') || t.includes('Error')) {
      console.log('[PAGE]', t);
    }
  });

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.evaluate(() => selectProject(0));
  await page.waitForTimeout(500);
  await page.evaluate(() => switchPage('requirement'));
  await page.waitForTimeout(500);
  await page.locator('#req-tabs .tab-item[data-tab="text"]').click();
  await page.waitForTimeout(300);
  await page.locator('#tab-text textarea').fill('TodoMVC应用:支持添加待办、标记完成、删除待办、按状态过滤列表');
  await page.waitForTimeout(300);

  console.log('===== 点击开始AI分析 =====');
  await page.locator('#page-requirement button:has-text("开始AI分析")').click();
  await page.waitForTimeout(10000);
  const page1 = await page.locator('.page.active').getAttribute('id');
  console.log('当前页:', page1);

  console.log('===== 点击确认并生成用例 =====');
  await page.locator('#page-analysis button:has-text("确认并生成用例")').click();
  await page.waitForTimeout(15000);
  const page2 = await page.locator('.page.active').getAttribute('id');
  console.log('当前页:', page2);

  // 检查后端用例
  const cases = await page.evaluate(() => fetch('http://localhost:8000/api/projects/1/testcases').then(r => r.json()));
  console.log('后端用例数:', cases.length);

  await browser.close();
})();
