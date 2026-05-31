from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.on(
        "console",
        lambda msg: print(
            f"CONSOLE [{msg.type}] {msg.text}"
        )
    )

    page.on(
        "pageerror",
        lambda err: print(
            f"PAGEERROR {err}"
        )
    )

    page.on(
        "requestfailed",
        lambda req: print(
            f"FAILED {req.url} -> {req.failure}"
        )
    )

    page.goto(
        "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"
    )

    page.wait_for_timeout(60000)

    print("TITLE:", page.title())

    browser.close()
