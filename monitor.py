from playwright.sync_api import sync_playwright

URL = "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.on("console", lambda msg: print(f"CONSOLE [{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: print(f"PAGEERROR {err}"))
    page.on("requestfailed", lambda req: print(f"FAILED {req.url} -> {req.failure}"))

    print("打开页面...")

    page.goto(URL, wait_until="domcontentloaded")

    try:
        page.wait_for_response(
            lambda r: "on6q7.wbstudiotour.com/fc/init-load" in r.url,
            timeout=30000
        )
        print("init-load 有响应")
    except Exception as e:
        print("init-load 等待失败:", e)

    page.wait_for_timeout(60000)

    print("TITLE:", page.title())
    print("URL:", page.url)

    print("BODY:")
    print(page.locator("body").inner_text()[:2000])

    browser.close()
