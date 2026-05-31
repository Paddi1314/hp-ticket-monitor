from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"
    )

    page.wait_for_timeout(10000)

    print("标题：", page.title())

    print("URL：", page.url)

    print("\n===== LocalStorage =====")

    print(page.evaluate("""
        () => {
            let r = {};
            for(let i=0;i<localStorage.length;i++){
                let k = localStorage.key(i);
                r[k] = localStorage.getItem(k);
            }
            return r;
        }
    """))

    browser.close()
