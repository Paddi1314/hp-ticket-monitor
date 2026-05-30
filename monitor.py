import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

message = "✅ GitHub Actions 测试成功"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

r = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(r.text)
