from playwright.sync_api import sync_playwright
import json

URL = "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    print("打开页面...")
    page.goto(URL, wait_until="networkidle")

    print("标题：", page.title())
    print("URL：", page.url)

    print("\n等待15秒...\n")
    page.wait_for_timeout(15000)

    # Arkose状态
    try:
        arkose_info = page.evaluate("""
        () => {
            if (typeof Arkose === "undefined") {
                return {
                    exists: false
                };
            }

            return {
                exists: true,
                version: Arkose.version,
                config: Arkose.getConfig(),
                dataResponse:
                    typeof Arkose.dataResponse === "function"
                        ? Arkose.dataResponse()
                        : null
            };
        }
        """)

        print("===== Arkose =====")
        print(json.dumps(arkose_info, indent=2, default=str))

    except Exception as e:
        print("Arkose读取失败:", e)

    # LocalStorage
    try:
        storage = page.evaluate("""
        () => {
            let result = {};
            for(let i=0;i<localStorage.length;i++){
                let k = localStorage.key(i);
                result[k] = localStorage.getItem(k);
            }
            return result;
        }
        """)

        print("\n===== LocalStorage =====")
        print(json.dumps(storage, indent=2))

    except Exception as e:
        print("LocalStorage失败:", e)

    # Cookie
    try:
        cookies = page.context.cookies()

        print("\n===== Cookies =====")
        print(json.dumps(cookies, indent=2))

    except Exception as e:
        print("Cookie失败:", e)

    # Script列表
    try:
        scripts = page.evaluate("""
        () => Array.from(document.scripts).map(x => x.src)
        """)

        print("\n===== Scripts =====")
        for s in scripts:
            print(s)

    except Exception as e:
        print("Script失败:", e)

    # 页面里有没有verifyBotProtectionToken
    try:
        html = page.content()

        print("\n===== 关键字检查 =====")

        for keyword in [
            "verifyBotProtectionToken",
            "createNewSession",
            "Arkose",
            "bp_token"
        ]:
            print(keyword, keyword in html)

    except Exception as e:
        print("HTML检查失败:", e)

    print("\n再等待30秒...\n")
    page.wait_for_timeout(30000)

    # 再查一次Arkose
    try:
        arkose_info2 = page.evaluate("""
        () => {
            if (typeof Arkose === "undefined") {
                return null;
            }

            return {
                version: Arkose.version,
                dataResponse:
                    typeof Arkose.dataResponse === "function"
                        ? Arkose.dataResponse()
                        : null
            };
        }
        """)

        print("===== 30秒后Arkose =====")
        print(json.dumps(arkose_info2, indent=2, default=str))

    except Exception as e:
        print("二次Arkose检查失败:", e)

    browser.close()
