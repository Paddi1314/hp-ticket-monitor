from playwright.sync_api import sync_playwright

URL = "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    )

    context = browser.new_context(
        viewport={"width": 1707, "height": 960},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        ),
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )

    page = context.new_page()

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    page.on("console", lambda msg: print(f"CONSOLE [{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: print(f"PAGEERROR {err}"))
    page.on("requestfailed", lambda req: print(f"FAILED {req.url} -> {req.failure}"))

    print("打开页面...")
    page.goto(URL, wait_until="domcontentloaded")

    page.wait_for_timeout(90000)

    print("TITLE:", page.title())
    print("URL:", page.url)

    print("BODY:")
    print(page.locator("body").inner_text()[:2000])

    print("navigator.webdriver:", page.evaluate("navigator.webdriver"))

    browser.close()
