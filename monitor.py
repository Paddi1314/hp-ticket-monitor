from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"
    )

    page.wait_for_timeout(10000)

    print(
        page.evaluate("""
        () => {
            return {
                arkose: typeof Arkose,
                selector: document.querySelector("#arkose-ec") !== null,
                body: document.body.innerHTML.includes("arkose"),
                scripts: [...document.scripts].map(x=>x.src)
            }
        }
        """)
    )

    browser.close()
