from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1",
        wait_until="networkidle"
    )

    print("标题：", page.title())
    print("当前URL：", page.url)

    print("\n等待60秒...\n")

    page.wait_for_timeout(60000)

    print("60秒后标题：", page.title())
    print("60秒后URL：", page.url)

    browser.close()
