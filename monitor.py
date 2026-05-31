import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

BASE_URL = "https://book.wbstudiotour.com"


def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


session = requests.Session()

# 第一步：创建 Session
r = session.post(
    f"{BASE_URL}/api/createNewSession",
    data={
        "site_id": 1,
        "event_type_id": 2,
        "device_type": "Desktop",
        "resolution_width": 1920,
        "resolution_height": 1080,
        "user_agent": "Mozilla/5.0"
    }
)

print("createNewSession:")
print(r.text)

data = r.json()["data"][0]

session_id = data["session_id"]
secret = data["secret"]

# 第二步：激活 Session
r = session.post(
    f"{BASE_URL}/api/getSessionState",
    headers={
        "X-Requested-With": "XMLHttpRequest"
    },
    data={
        "session_id": session_id,
        "secret": secret
    }
)

print("getSessionState:")
print(r.text)

# 第三步：查询 2026-07-26
r = session.post(
    f"{BASE_URL}/api/getEvents",
    headers={
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    },
    json={
        "session_id": session_id,
        "secret": secret,
        "site_id": 1,
        "ticket_count": 0,
        "event_id": 2,
        "start_date": "2026-07-26",
        "end_date": "2026-07-26"
    }
)

print("getEvents:")
print(r.text)

result = r.json()

if not result.get("success"):
    send_telegram("❌ 查询失败")
    raise SystemExit()

slots = result["data"]

found = []

for slot in slots:

    start_time = slot["startTime"]
    available = slot["available"]

    if available > 0 and start_time <= "14:30":

        found.append(
            f"{start_time} 剩余 {available} 张"
        )

if found:

    send_telegram(
        "🎉 发现 7月26日 14:30前门票！\n\n"
        + "\n".join(found)
    )

else:

    print("No tickets")
