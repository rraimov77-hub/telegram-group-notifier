import requests
from flask import Flask, request
from datetime import datetime

TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"
YOUR_CHAT_ID = 1008219132

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:

        # Новый участник
        if "new_chat_members" in data["message"]:
            for user in data["message"]["new_chat_members"]:

                name = user.get("first_name", "Без имени")
                username = user.get("username", "нет username")
                user_id = user.get("id")
                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                text = f"""
📥 Новый участник!

👤 Имя: {name}
🔗 Username: @{username}
🆔 ID: {user_id}
⏰ Время: {time_now}
"""

                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(url, data={
                    "chat_id": YOUR_CHAT_ID,
                    "text": text
                })

    return "OK"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
