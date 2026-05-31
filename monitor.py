from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1",
        wait_until="networkidle"
    )

    print("标题：", page.title())
    print("当前URL：", page.url)

    # 看看页面源码前1000个字符
    html = page.content()

    print("\n===== 页面源码前1000字符 =====\n")
    print(html[:1000])

    browser.close()
