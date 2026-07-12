const { chromium } = require('playwright');
const HTML_PATH = 'e:\\hkx_project\\TestPilot\\AI测试智能体_TestPilot.html';
const URL = 'file:///' + HTML_PATH.replace(/\\/g, '/');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  const errors = [];
  page.on('console', msg => {
    const t = msg.text();
    if (t.includes('持久化') || t.includes('已持久化') || t.includes('持久化失败') || t.includes('Generate') || t.includes('projectId') || t.includes('cases')) {
      console.log('[PAGE]', t);
    }
  });
  page.on('pageerror', err => errors.push(String(err)));

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.evaluate(() => selectProject(0));
  await page.waitForTimeout(500);

  // 模拟一次完整的 generate 流程:手动设置 currentAnalysisResult,然后调用 handleGenerateTestcases
  console.log('===== 直接调用 handleGenerateTestcases 测试持久化 =====');
  const result = await page.evaluate(async () => {
    // 设置一个假的 analysisResult
    currentAnalysisResult = {
      feature_points: [{
        name: '测试功能',
        priority: 'P0',
        test_dimensions: ['功能测试'],
        business_logic: '测试逻辑',
        risk_hint: ''
      }],
      requirementId: null,
      estimated_case_count: 2
    };
    const pid = getCurrentProjectId();
    console.log('projectId=', pid);
    // 手动构造 generate 结果来测试持久化
    const fakeResult = {
      cases: [{
        title: '持久化测试用例',
        module: 'test',
        priority: 'P0',
        precondition: '无',
        steps: ['步骤1'],
        expected: '预期1',
        script: "test('demo', () => { expect(1).toBe(1); });"
      }]
    };
    // 测试 createTestCase
    try {
      const saved = await TestPilotAPI.createTestCase(pid, {
        title: fakeResult.cases[0].title,
        module: fakeResult.cases[0].module,
        priority: fakeResult.cases[0].priority,
        precondition: fakeResult.cases[0].precondition,
        steps: fakeResult.cases[0].steps,
        expected: fakeResult.cases[0].expected,
        script: fakeResult.cases[0].script
      });
      console.log('保存成功, id=', saved.id);
      return { ok: true, id: saved.id, pid: pid };
    } catch (e) {
      console.log('保存失败:', e.message);
      return { ok: false, err: e.message, pid: pid };
    }
  });
  console.log('结果:', JSON.stringify(result));

  await browser.close();
})();
