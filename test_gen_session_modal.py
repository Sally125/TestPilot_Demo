"""测试生成会话弹窗：切换脚本模式并截图"""
import urllib.parse
from playwright.sync_api import sync_playwright

frontend_url = 'http://localhost:8080/' + urllib.parse.quote('AI测试智能体_TestPilot.html')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})

    # 捕获 console 错误
    errors = []
    page.on('console', lambda msg: errors.append(f'[{msg.type}] {msg.text}') if msg.type in ['error', 'warning'] else None)

    print(f'1. 打开页面: {frontend_url}')
    page.goto(frontend_url)
    page.wait_for_load_state('networkidle', timeout=15000)
    page.wait_for_timeout(1500)

    # 截图1：首页
    page.screenshot(path='test_screenshot_1_home.png', full_page=False)
    print('   截图1: 首页已保存')

    # 2. 找到第一个项目并点击（展开操作菜单）
    print('2. 查找登录态配置入口...')

    # 直接点击侧边栏的"登录态配置"或顶部按钮
    # 先尝试查找登录态管理入口
    login_config_btn = page.locator('text=登录态').first
    if login_config_btn.count() > 0:
        print(f'   找到登录态按钮: {login_config_btn.text_content()}')
        login_config_btn.click()
        page.wait_for_timeout(1000)
    else:
        # 尝试通过执行中心进入
        print('   未找到直接入口，尝试执行中心...')
        exec_btn = page.locator('text=执行中心').first
        if exec_btn.count() > 0:
            exec_btn.click()
            page.wait_for_timeout(1000)

    # 截图2：尝试打开登录态管理
    page.screenshot(path='test_screenshot_2_login_config.png', full_page=False)

    # 3. 查找"管理登录态"或"登录态配置"按钮
    print('3. 查找管理登录态按钮...')
    manage_btns = page.locator('text=管理登录态')
    print(f'   找到 {manage_btns.count()} 个管理登录态按钮')
    if manage_btns.count() > 0:
        manage_btns.first.click()
        page.wait_for_timeout(1500)

    # 截图3：登录态管理面板
    page.screenshot(path='test_screenshot_3_profiles_panel.png', full_page=False)
    print('   截图3: 登录态管理面板已保存')

    # 4. 查找"生成会话"或"重新生成"按钮
    print('4. 查找生成会话按钮...')
    gen_btns = page.locator('text=生成会话')
    regen_btns = page.locator('text=重新生成')
    total = gen_btns.count() + regen_btns.count()
    print(f'   生成会话: {gen_btns.count()} 个, 重新生成: {regen_btns.count()} 个')

    if gen_btns.count() > 0:
        gen_btns.first.click()
        page.wait_for_timeout(1500)
    elif regen_btns.count() > 0:
        regen_btns.first.click()
        page.wait_for_timeout(1500)
    else:
        print('   未找到生成会话按钮，尝试编辑第一个登录态...')
        # 可能需要先创建一个登录态
        # 查找新增按钮
        add_btn = page.locator('text=新增登录态').first
        if add_btn.count() > 0:
            add_btn.click()
            page.wait_for_timeout(1000)
            page.screenshot(path='test_screenshot_4_add_form.png', full_page=False)
            print('   截图4: 新增表单已保存')

    # 截图4：生成会话弹窗
    page.screenshot(path='test_screenshot_4_gen_session_modal.png', full_page=False)
    print('   截图4: 生成会话弹窗已保存')

    # 5. 查找模式切换按钮
    print('5. 查找脚本模式切换按钮...')
    custom_btn = page.locator('#gs-mode-custom-btn')
    form_btn = page.locator('#gs-mode-form-btn')
    print(f'   脚本模式按钮: {custom_btn.count()} 个, 表单模式按钮: {form_btn.count()} 个')

    if custom_btn.count() > 0:
        print('   点击脚本模式按钮...')
        custom_btn.click()
        page.wait_for_timeout(1000)

        # 截图5：脚本模式
        page.screenshot(path='test_screenshot_5_custom_mode.png', full_page=False)
        print('   截图5: 脚本模式已保存')

        # 6. 点击插入模板
        print('6. 查找插入模板按钮...')
        template_btn = page.locator('text=插入模板')
        print(f'   插入模板按钮: {template_btn.count()} 个')
        if template_btn.count() > 0:
            template_btn.first.click()
            page.wait_for_timeout(500)

            # 截图6：插入模板后
            page.screenshot(path='test_screenshot_6_template_inserted.png', full_page=False)
            print('   截图6: 模板已插入')

            # 读取 textarea 内容
            textarea = page.locator('#gs-custom-script')
            if textarea.count() > 0:
                value = textarea.input_value()
                print(f'   脚本内容长度: {len(value)}')
                print(f'   脚本前100字: {value[:100]}')
    else:
        print('   ✗ 未找到脚本模式切换按钮！')
        # 打印当前弹窗的 HTML 帮助诊断
        modal = page.locator('#generate-session-modal')
        if modal.count() > 0:
            html = modal.inner_html()
            print(f'   弹窗 HTML 前500字: {html[:500]}')

    # 输出 console 错误
    if errors:
        print(f'\nConsole 错误/警告 ({len(errors)} 条):')
        for e in errors[:10]:
            print(f'  {e}')
    else:
        print('\n无 Console 错误')

    browser.close()
    print('\n测试完成')
