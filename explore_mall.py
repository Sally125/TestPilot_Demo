"""探索 newbee-mall 商品详情链接模式"""
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:28089"
CHROME = r"C:\Users\zsy_cusci\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto(APP_URL, wait_until="networkidle")
    page.wait_for_timeout(1500)

    # 找所有不重复的 href 模式
    hrefs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href')).filter(h => h && !h.startsWith('#'));
    }""")
    patterns = {}
    for h in hrefs:
        # 归类
        key = h.split(';')[0].split('?')[0]
        patterns[key] = patterns.get(key, 0) + 1
    print("链接模式:")
    for k, v in sorted(patterns.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    # 找商品详情类链接（含数字 id 的 /goods 或 /detail）
    detail_links = page.locator("a[href*='detail'], a[href*='/goods/']").all()
    print(f"\n详情链接数: {len(detail_links)}")
    for i, l in enumerate(detail_links[:3]):
        print(f"  href={l.get_attribute('href')}")

    browser.close()
