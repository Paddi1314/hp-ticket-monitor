from playwright.sync_api import sync_playwright
import json

URL = "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("打开页面...")
    page.goto(URL, wait_until="networkidle")

    print("标题：", page.title())
    print("URL：", page.url)

    print("\n等待15秒...\n")
    page.wait_for_timeout(15000)

    info = page.evaluate("""
    () => {
        return {
            title: document.title,
            url: location.href,
            bodyText: document.body.innerText.slice(0, 3000),
            buttons: Array.from(document.querySelectorAll("button")).map(b => b.innerText),
            links: Array.from(document.querySelectorAll("a")).map(a => ({
                text: a.innerText,
                href: a.href
            })),
            arkoseDiv: document.querySelector("#arkose-ec") !== null,
            arkoseExists: typeof Arkose !== "undefined",
            arkoseConfig: typeof Arkose !== "undefined" ? Arkose.getConfig() : null,
            arkoseDataResponse: (
                typeof Arkose !== "undefined" &&
                typeof Arkose.dataResponse === "function"
            ) ? Arkose.dataResponse() : null
        };
    }
    """)

    print("\n===== 页面状态 =====")
    print(json.dumps(info, indent=2, default=str))

    print("\n等待30秒后再检查一次...\n")
    page.wait_for_timeout(30000)

    info2 = page.evaluate("""
    () => {
        return {
            title: document.title,
            url: location.href,
            bodyText: document.body.innerText.slice(0, 3000),
            buttons: Array.from(document.querySelectorAll("button")).map(b => b.innerText),
            arkoseDataResponse: (
                typeof Arkose !== "undefined" &&
                typeof Arkose.dataResponse === "function"
            ) ? Arkose.dataResponse() : null
        };
    }
    """)

    print("\n===== 30秒后页面状态 =====")
    print(json.dumps(info2, indent=2, default=str))

    browser.close()
