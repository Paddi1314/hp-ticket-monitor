from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"
    )

    page.wait_for_timeout(10000)

    print("Arkose对象:")

    print(
        page.evaluate("""
        () => {
            if (!window.Arkose)
                return "Arkose不存在";

            return {
                version: Arkose.version,
                config: Arkose.getConfig()
            };
        }
        """)
    )

    browser.close()
