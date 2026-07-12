const { chromium } = require('playwright');
const HTML_PATH = 'e:\\hkx_project\\TestPilot\\AI测试智能体_TestPilot.html';
const URL = 'file:///' + HTML_PATH.replace(/\\/g, '/');
const API = 'http://localhost:8000/api';

const apiPost = (path, body) => fetch(`${API}${path}`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) }).then(r => r.json());

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on('console', msg => { const t = msg.text(); if (t.includes('[') || t.includes('持久化') || t.includes('Generate') || t.includes('Analysis') || t.includes('Execution') || t.includes('error')) console.log('[PAGE]', t); });
  page.on('pageerror', err => console.log('[JS ERROR]', String(err)));

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.evaluate(() => selectProject(0));
  await page.waitForTimeout(500);

  // Step 1: AI 分析(等待 loading 消失)
  console.log('\n===== 1. 需求分析 =====');
  await page.evaluate(() => switchPage('requirement'));
  await page.waitForTimeout(500);
  await page.locator('#req-tabs .tab-item[data-tab="text"]').click();
  await page.locator('#tab-text textarea').fill('TodoMVC应用:支持添加待办、标记完成、删除待办');
  await page.locator('#page-requirement button:has-text("开始AI分析")').click();
  // 等待 loading 出现
  await page.waitForSelector('#api-loading', { state: 'visible', timeout: 5000 }).catch(() => {});
  // 等待 loading 消失
  await page.waitForSelector('#api-loading', { state: 'hidden', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(1000);
  const p1 = await page.locator('.page.active').getAttribute('id');
  console.log('分析后页:', p1);

  // Step 2: 生成用例(等待 loading 消失)
  console.log('\n===== 2. 生成用例 =====');
  await page.locator('#page-analysis button:has-text("确认并生成用例")').click();
  await page.waitForSelector('#api-loading', { state: 'visible', timeout: 5000 }).catch(() => {});
  await page.waitForSelector('#api-loading', { state: 'hidden', timeout: 90000 }).catch(() => {});
  await page.waitForTimeout(1000);
  const p2 = await page.locator('.page.active').getAttribute('id');
  console.log('生成后页:', p2);

  const cases = await page.evaluate(() => fetch(`${API}/projects/1/testcases`).then(r=>r.json()));
  console.log('后端用例数:', cases.length);

  // Step 3: 执行
  console.log('\n===== 3. 执行用例 =====');
  if (p2 === 'page-testcases' && await page.locator('#page-testcases .case-card .checkbox').count() > 0) {
    await page.locator('#page-testcases .case-card .checkbox').first().check();
    await page.waitForTimeout(300);
    await page.locator('#page-testcases button:has-text("执行选中用例")').click();
    await page.waitForSelector('#api-loading', { state: 'visible', timeout: 5000 }).catch(() => {});
    await page.waitForSelector('#api-loading', { state: 'hidden', timeout: 120000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const p3 = await page.locator('.page.active').getAttribute('id');
    console.log('执行后页:', p3);
  } else {
    console.log('未到用例库或无 checkbox,跳过执行');
  }

  const execs = await page.evaluate(() => fetch(`${API}/projects/1/executions`).then(r=>r.json()));
  const records = await page.evaluate(() => fetch(`${API}/projects/1/execution-records`).then(r=>r.json()));
  console.log('执行批次数:', execs.length, '| 执行记录数:', records.length);

  // Step 4: 刷新验证
  console.log('\n===== 4. 刷新页面验证数据加载 =====');
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.evaluate(() => selectProject(0));
  await page.waitForTimeout(500);

  await page.evaluate(() => switchPage('requirement'));
  await page.waitForTimeout(2000);
  const reqRows = await page.locator('#page-requirement table tbody tr').count();
  console.log('历史需求行数:', reqRows);

  await page.evaluate(() => switchPage('testcases'));
  await page.waitForTimeout(2000);
  const caseCards = await page.locator('#page-testcases .case-card').count();
  console.log('用例库卡片数:', caseCards);

  await page.evaluate(() => switchPage('execution'));
  await page.waitForTimeout(2000);
  const execItems = await page.locator('#page-execution .exec-item').count();
  console.log('执行条目数:', execItems);

  await page.evaluate(() => switchPage('report'));
  await page.waitForTimeout(2000);
  const passRate = await page.locator('#page-report .stat-value.primary').first().textContent().catch(() => 'N/A');
  console.log('报告通过率:', passRate);

  await page.screenshot({ path: 'e:/hkx_project/TestPilot/persistence_final.png' });
  await browser.close();
  console.log('\n===== 完成 =====');
})();
