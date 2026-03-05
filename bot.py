import requests
from flask import Flask, request
from datetime import datetime
import threading
import time
import pytz
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
       
        # 📊 Команда статистики
        if "text" in data["message"] and data["message"]["text"].lower() == "статистика":

    try:
        with open("stats.txt", "r") as f:
            data_stats = f.read().split(",")
            joined = int(data_stats[0])
            left = int(data_stats[1])
    except:
        joined = 0
        left = 0

    net = joined - left

    text = f"""📊 Статистика

➕ Пришло: {joined}
➖ Ушло: {left}
📈 Прирост: {net}
"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": YOUR_CHAT_ID,
        "text": text
    })
        # 📥 Новый участник
        if "new_chat_members" in data["message"]:
            for user in data["message"]["new_chat_members"]:

                name = user.get("first_name", "Без имени")
                username = user.get("username")
                user_id = user.get("id")
                tz = pytz.timezone("Asia/Tashkent")
                time_now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
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
                update_stats(joined=1)      
        # 📤 Участник вышел
        if "left_chat_member" in data["message"]:

            user = data["message"]["left_chat_member"]
            name = user.get("first_name", "Без имени")
            user_id = user.get("id")
            tz = pytz.timezone("Asia/Tashkent")
            time_now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

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
            update_stats(left=1)
    return "OK"


@app.route("/")
def home():
    return "Bot is running"

def daily_report_scheduler():
    while True:
        now = datetime.now()

        # Если время 23:00
        if now.hour == 23 and now.minute == 0:
            try:
                with open("stats.txt", "r") as f:
                    data = f.read().split(",")
                    joined = int(data[0])
                    left = int(data[1])
            except:
                joined = 0
                left = 0

            net = joined - left

            text = f"""📊 Статистика за день

➕ Пришло: {joined}
➖ Ушло: {left}
📈 Прирост: {net}
"""

            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url, data={
                "chat_id": YOUR_CHAT_ID,
                "text": text
            })

            # Сброс
            with open("stats.txt", "w") as f:
                f.write("0,0")

            time.sleep(60)

        time.sleep(30)
if __name__ == "__main__":
    thread = threading.Thread(target=daily_report_scheduler)
    thread.daemon = True
    thread.start()

    app.run(host="0.0.0.0", port=10000)
