// 测试"生成会话"弹窗：脚本模式切换 + 插入模板 + 开始生成
// 流程：用例库 → 前往执行中心 → 登录态配置 → 生成会话 → 切换脚本模式 → 插入模板 → 开始生成会话
const { chromium } = require('playwright');

const frontendUrl = 'http://localhost:8080/AI%E6%B5%8B%E8%AF%95%E6%99%BA%E8%83%BD%E4%BD%93_TestPilot.html';
const SCREENSHOT_DIR = 'e:\\hkx_project\\TestPilot\\test_snapshot';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  // 捕获 console 错误
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(`[error] ${msg.text()}`);
  });
  page.on('pageerror', err => errors.push(`[pageerror] ${err.message}`));

  const log = (msg) => console.log(`[${new Date().toLocaleTimeString()}] ${msg}`);

  try {
    log('1. 打开页面: ' + frontendUrl);
    await page.goto(frontendUrl, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);

    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_1_home.png` });
    log('   截图1: 首页已保存');

    // 2. 直接打开执行中心模态框（openExecutionModal 是全局函数）
    log('2. 调用 openExecutionModal() 打开执行中心...');
    const execModalState = await page.evaluate(() => {
      openExecutionModal();
      const m = document.getElementById('execution-modal');
      return {
        exists: !!m,
        hasShowClass: m ? m.classList.contains('show') : false,
        display: m ? getComputedStyle(m).display : 'n/a',
        bodyContent: m ? (m.querySelector('#execution-modal-body') || {}).innerHTML?.length : 0,
      };
    });
    log('   模态框状态: ' + JSON.stringify(execModalState));
    await page.waitForTimeout(1500);

    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_2_exec_center.png` });
    log('   截图2: 执行中心已保存');

    // 3. 调用 showLoginConfig() 打开登录态配置面板
    log('3. 调用 showLoginConfig()...');
    await page.evaluate(() => {
      if (typeof showLoginConfig === 'function') showLoginConfig();
    });
    await page.waitForTimeout(1500);

    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_3_login_profiles.png` });
    log('   截图3: 登录态配置面板已保存');

    // 5. 点击"生成会话"按钮（profile id=2，状态 ungenerated）
    log('5. 点击"生成会话"按钮...');
    const genBtn = page.locator('button:has-text("生成会话")').first();
    const regenBtn = page.locator('button:has-text("重新生成")').first();
    let clicked = false;
    if (await genBtn.count() > 0 && await genBtn.first().isVisible()) {
      await genBtn.first().click();
      clicked = true;
      log('   已点击"生成会话"');
    } else if (await regenBtn.count() > 0 && await regenBtn.first().isVisible()) {
      await regenBtn.first().click();
      clicked = true;
      log('   已点击"重新生成"');
    }
    if (!clicked) {
      log('   ✗ 未找到生成会话按钮，尝试直接调用 showGenerateSessionGuide(2)');
      await page.evaluate(() => showGenerateSessionGuide(2));
    }
    await page.waitForTimeout(1000);

    // 6. 验证弹窗已打开
    log('6. 验证弹窗已打开...');
    const modal = page.locator('#generate-session-modal');
    await modal.waitFor({ state: 'visible', timeout: 5000 });
    log('   ✓ 弹窗已打开');

    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_5_modal_form_mode.png` });
    log('   截图5: 弹窗(默认表单模式)已保存');

    // 7. 验证表单模式元素存在
    log('7. 验证弹窗元素...');
    const formBtn = page.locator('#gs-mode-form-btn');
    const customBtn = page.locator('#gs-mode-custom-btn');
    const formModeDiv = page.locator('#gs-form-mode');
    const customModeDiv = page.locator('#gs-custom-mode');
    log('   表单模式按钮存在: ' + (await formBtn.count() > 0));
    log('   脚本模式按钮存在: ' + (await customBtn.count() > 0));
    log('   表单区可见: ' + (await formModeDiv.isVisible()));
    log('   脚本区可见: ' + (await customModeDiv.isVisible()));

    // 8. 点击"脚本模式"按钮
    log('8. 点击"脚本模式"按钮...');
    await customBtn.click();
    await page.waitForTimeout(800);

    log('   切换后 - 表单区可见: ' + (await formModeDiv.isVisible()));
    log('   切换后 - 脚本区可见: ' + (await customModeDiv.isVisible()));

    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_6_custom_mode.png` });
    log('   截图6: 脚本模式已保存');

    // 9. 验证脚本区元素
    const scriptTextarea = page.locator('#gs-custom-script');
    const insertTplBtn = page.locator('button:has-text("插入模板")');
    log('   脚本编辑框存在: ' + (await scriptTextarea.count() > 0));
    log('   插入模板按钮存在: ' + (await insertTplBtn.count() > 0));

    // 读取当前 textarea 内容（应该为空）
    const beforeValue = await scriptTextarea.inputValue();
    log('   插入前脚本内容长度: ' + beforeValue.length);

    // 10. 点击"插入模板"
    log('10. 点击"插入模板"...');
    await insertTplBtn.first().click();
    await page.waitForTimeout(500);

    const afterValue = await scriptTextarea.inputValue();
    log('   插入后脚本内容长度: ' + afterValue.length);
    log('   脚本前80字: ' + afterValue.substring(0, 80).replace(/\n/g, '\\n'));

    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_7_template_inserted.png` });
    log('   截图7: 模板已插入');

    // 11. 点击"开始生成会话"，验证先保存配置再执行
    log('11. 点击"开始生成会话"...');
    const startBtn = page.locator('#gen-session-start-btn');
    await startBtn.click();
    await page.waitForTimeout(1500);

    // 截图保存配置/生成中的状态
    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_8_saving_config.png` });
    log('   截图8: 保存配置/生成中状态已保存');

    const statusDiv = page.locator('#gen-session-status');
    if (await statusDiv.isVisible()) {
      const statusText = await statusDiv.textContent();
      log('   状态文本: ' + statusText.replace(/\s+/g, ' ').trim().substring(0, 120));
    }

    // 等待一会儿看执行结果（最多 20 秒）
    log('12. 等待执行结果（最多20秒）...');
    for (let i = 0; i < 10; i++) {
      await page.waitForTimeout(2000);
      const btnText = await startBtn.textContent();
      log('   按钮文本: ' + btnText);
      if (btnText.includes('完成') || btnText.includes('重试')) {
        break;
      }
    }

    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_9_result.png` });
    log('   截图9: 执行结果已保存');

    if (await statusDiv.isVisible()) {
      const statusText = await statusDiv.textContent();
      log('   最终状态: ' + statusText.replace(/\s+/g, ' ').trim().substring(0, 200));
    }

    // 切回表单模式截图（展示切换功能）
    log('13. 切回表单模式...');
    await formBtn.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_10_back_to_form.png` });
    log('   截图10: 切回表单模式已保存');

  } catch (e) {
    log('✗ 测试异常: ' + e.message);
    await page.screenshot({ path: `${SCREENSHOT_DIR}\\gs_shot_error.png` }).catch(() => {});
  }

  // 输出 console 错误
  if (errors.length > 0) {
    log('\nConsole 错误 (' + errors.length + ' 条):');
    errors.slice(0, 10).forEach(e => log('  ' + e));
  } else {
    log('\n无 Console 错误');
  }

  await browser.close();
  log('\n测试完成');
})();
