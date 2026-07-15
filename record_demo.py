"""录制 newbee-mall 关键操作演示视频（headed 模式 + Playwright video 录制）"""
import os
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:28089"
CHROME = r"C:\Users\zsy_cusci\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"
VIDEO_DIR = "e2e_reports/videos"

os.makedirs(VIDEO_DIR, exist_ok=True)


def smooth_scroll(page, positions, pause=1200):
    for y in positions:
        page.evaluate(f"window.scrollTo({{top: {y}, behavior: 'smooth'}})")
        page.wait_for_timeout(pause)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, executable_path=CHROME, args=["--start-maximized"])
    context = browser.new_context(
        record_video_dir=VIDEO_DIR,
        record_video_size={"width": 1280, "height": 720},
        viewport={"width": 1280, "height": 720},
    )
    page = context.new_page()

    try:
        # ===== 1. 首页浏览 =====
        print("[录屏] 1/5 访问首页...")
        page.goto(APP_URL, wait_until="networkidle")
        page.wait_for_timeout(2500)
        smooth_scroll(page, [400, 800, 1200, 1600, 1200, 600, 0])

        # ===== 2. 进入商品详情 =====
        print("[录屏] 2/5 进入商品详情页...")
        first_goods = page.locator("a[href*='/goods/detail/']").first
        first_goods.scroll_into_view_if_needed()
        page.wait_for_timeout(1200)
        first_goods.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2500)
        smooth_scroll(page, [300, 600, 900, 500, 0], pause=1000)

        # ===== 3. 返回首页 =====
        print("[录屏] 3/5 返回首页...")
        page.go_back()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # ===== 4. 访问登录页 =====
        print("[录屏] 4/5 访问登录页...")
        page.goto(f"{APP_URL}/login", wait_until="networkidle")
        page.wait_for_timeout(2500)

        # ===== 5. 访问注册页 =====
        print("[录屏] 5/5 访问注册页...")
        page.goto(f"{APP_URL}/register", wait_until="networkidle")
        page.wait_for_timeout(2500)

    except Exception as e:
        print(f"[录屏] 异常: {e}")
    finally:
        context.close()
        browser.close()

videos = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".webm")]
if videos:
    videos.sort(key=lambda f: os.path.getmtime(os.path.join(VIDEO_DIR, f)))
    latest = os.path.join(VIDEO_DIR, videos[-1])
    print(f"[录屏] 完成，视频已保存: {latest}")
    print(f"[录屏] 文件大小: {os.path.getsize(latest) / 1024:.1f} KB")
