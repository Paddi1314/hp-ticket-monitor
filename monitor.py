import os
import json
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

TARGET_DATE = "2026-07-26"
TARGET_LATEST_TIME = "14:30"
URL = "https://book.wbstudiotour.com/?event_type_id=2&language_id=1&site_id=1"


def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=20
    )


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
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

    session_info = {}

    def handle_response(response):
        if "/api/createNewSession" in response.url:
            try:
                data = response.json()
                if data.get("success") and data.get("data"):
                    session_info["session_id"] = data["data"][0]["session_id"]
                    session_info["secret"] = data["data"][0]["secret"]
                    print("抓到 session:", session_info)
            except Exception as e:
                print("读取 session 失败:", e)

    page.on("response", handle_response)

    print("打开页面...")
    page.goto(URL, wait_until="domcontentloaded")

    try:
        page.wait_for_url("**/tickets?language_id=1", timeout=90000)
    except Exception:
        print("未进入 tickets，当前：", page.title(), page.url)

    print("标题：", page.title())
    print("URL：", page.url)

    page.wait_for_timeout(5000)

    if "tickets" not in page.url:
        send_telegram("⚠️ 监控失败：没有通过 Queue。")
        browser.close()
        raise SystemExit()

    if not session_info:
        page.wait_for_timeout(10000)

    if not session_info:
        send_telegram("❌ 监控失败：没有抓到 session。")
        browser.close()
        raise SystemExit()

    result = page.evaluate(
        """async ({sessionId, secret, targetDate}) => {
            const stateRes = await fetch("https://book.wbstudiotour.com/api/getSessionState", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: new URLSearchParams({
                    session_id: String(sessionId),
                    secret: secret
                }).toString()
            });

            const stateText = await stateRes.text();

            const eventsRes = await fetch("https://book.wbstudiotour.com/api/getEvents", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    secret: secret,
                    site_id: 1,
                    ticket_count: 0,
                    event_id: 2,
                    start_date: targetDate,
                    end_date: targetDate
                })
            });

            const eventsText = await eventsRes.text();

            return { stateText, eventsText };
        }""",
        {
            "sessionId": session_info["session_id"],
            "secret": session_info["secret"],
            "targetDate": TARGET_DATE
        }
    )

    print("查询结果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    browser.close()


events = json.loads(result["eventsText"])

if not events.get("success"):
    send_telegram("❌ getEvents 查询失败\n" + result["eventsText"][:1000])
    raise SystemExit()

matched = []

for slot in events.get("data", []):
    start_time = slot.get("startTime")
    available = int(slot.get("available", 0))

    if start_time <= TARGET_LATEST_TIME and available > 0:
        matched.append(f"{start_time} - {available} 张")

if matched:
    send_telegram(
        f"🎉 发现 {TARGET_DATE} {TARGET_LATEST_TIME} 前有票！\n\n"
        + "\n".join(matched)
        + "\n\n快去官网下单。"
    )
else:
    print(f"没有发现 {TARGET_DATE} {TARGET_LATEST_TIME} 前的票。")
