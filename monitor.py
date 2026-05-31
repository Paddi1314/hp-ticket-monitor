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
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
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

    print("等待进入 Tickets 页面...")
    try:
        page.wait_for_url("**/tickets?language_id=1", timeout=90000)
    except Exception:
        print("没有自动进入 Tickets 页面，当前：", page.title(), page.url)

    print("当前标题：", page.title())
    print("当前URL：", page.url)

    if "tickets" not in page.url:
        send_telegram("⚠️ 监控失败：没有通过 Queue，仍停留在排队页。")
        browser.close()
        raise SystemExit()

    print("创建新 Session 并查询票务...")

    result = page.evaluate(f"""
    async () => {{
        const createRes = await fetch("https://book.wbstudiotour.com/api/createNewSession", {{
            method: "POST",
            credentials: "include",
            headers: {{
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest"
            }},
            body: new URLSearchParams({{
                site_id: "1",
                event_type_id: "2",
                device_type: "Desktop",
                resolution_width: "1707",
                resolution_height: "960",
                user_agent: navigator.userAgent
            }}).toString()
        }});

        const createText = await createRes.text();

        let createJson;
        try {{
            createJson = JSON.parse(createText);
        }} catch (e) {{
            return {{
                ok: false,
                step: "createNewSession_parse",
                text: createText
            }};
        }}

        if (!createJson.success) {{
            return {{
                ok: false,
                step: "createNewSession",
                data: createJson
            }};
        }}

        const session = createJson.data[0];
        const sessionId = session.session_id;
        const secret = session.secret;

        const stateRes = await fetch("https://book.wbstudiotour.com/api/getSessionState", {{
            method: "POST",
            credentials: "include",
            headers: {{
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest"
            }},
            body: new URLSearchParams({{
                session_id: String(sessionId),
                secret: secret
            }}).toString()
        }});

        const stateText = await stateRes.text();

        const eventsRes = await fetch("https://book.wbstudiotour.com/api/getEvents", {{
            method: "POST",
            credentials: "include",
            headers: {{
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            }},
            body: JSON.stringify({{
                session_id: sessionId,
                secret: secret,
                site_id: 1,
                ticket_count: 0,
                event_id: 2,
                start_date: "{TARGET_DATE}",
                end_date: "{TARGET_DATE}"
            }})
        }});

        const eventsText = await eventsRes.text();

        let eventsJson;
        try {{
            eventsJson = JSON.parse(eventsText);
        }} catch (e) {{
            return {{
                ok: false,
                step: "getEvents_parse",
                session_id: sessionId,
                secret: secret,
                stateText: stateText,
                text: eventsText
            }};
        }}

        return {{
            ok: true,
            session_id: sessionId,
            secret: secret,
            stateText: stateText,
            events: eventsJson
        }};
    }}
    """)

    print("查询结果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    browser.close()


if not result.get("ok"):
    send_telegram(
        "❌ 监控失败\n"
        f"步骤：{result.get('step')}\n"
        f"内容：{str(result)[:1000]}"
    )
    raise SystemExit()


events = result["events"]

if not events.get("success"):
    send_telegram(
        "❌ getEvents 查询失败\n"
        f"{json.dumps(events, ensure_ascii=False)[:1000]}"
    )
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
