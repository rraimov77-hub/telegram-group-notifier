import requests
from flask import Flask, request
from datetime import datetime

# 🔹 ВСТАВЬТЕ СЮДА СВОЙ ТОКЕН
TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"

# 🔹 ВАШ TELEGRAM ID
YOUR_CHAT_ID = 1008219132
# Файл для хранения статистики
STATS_FILE = "stats.txt"

def update_stats(joined=0, left=0):
    try:
        with open(STATS_FILE, "r") as f:
            data = f.read().split(",")
            current_joined = int(data[0])
            current_left = int(data[1])
    except:
        current_joined = 0
        current_left = 0

    current_joined += joined
    current_left += left

    with open(STATS_FILE, "w") as f:
        f.write(f"{current_joined},{current_left}")
app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:

        # 📥 Новый участник
        if "new_chat_members" in data["message"]:
            for user in data["message"]["new_chat_members"]:

                name = user.get("first_name", "Без имени")
                username = user.get("username")
                user_id = user.get("id")
                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                text = (
                    "📥 Новый участник!\n\n"
                    f"👤 Имя: {name}\n"
                    f"🔗 Username: @{username if username else 'нет username'}\n"
                    f"🆔 ID: {user_id}\n"
                    f"⏰ Время: {time_now}"
                )

                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(url, data={
                    "chat_id": YOUR_CHAT_ID,
                    "text": text
                })

        # 📤 Участник вышел
        if "left_chat_member" in data["message"]:

            user = data["message"]["left_chat_member"]
            name = user.get("first_name", "Без имени")
            user_id = user.get("id")
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            text = (
                "📤 Участник вышел!\n\n"
                f"👤 Имя: {name}\n"
                f"🆔 ID: {user_id}\n"
                f"⏰ Время: {time_now}"
            )

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
