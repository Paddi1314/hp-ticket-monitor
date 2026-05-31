import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SESSION_ID = "7373385898"
SECRET = "yaihjanwndsdttt"

s = requests.Session()

url = "https://book.wbstudiotour.com/api/getEvents"

payload = {
    "session_id": int(SESSION_ID),
    "secret": SECRET,
    "site_id": 1,
    "ticket_count": 0,
    "event_id": 2,
    "start_date": "2026-07-26",
    "end_date": "2026-07-26"
}

r = s.post(url, json=payload)

print(r.text)

data = r.json()

if data.get("success"):

    events = data.get("data", [])

    found = False

    for e in events:

        if e["startTime"] <= "14:30" and e["available"] > 0:

            found = True

            msg = (
                f"🎉 发现票！\n"
                f"时间: {e['startTime']}\n"
                f"余票: {e['available']}"
            )

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": msg
                }
            )

    if not found:
        print("没有目标票")

else:
    print("查询失败")
