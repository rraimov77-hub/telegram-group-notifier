import os
import requests
from flask import Flask, request
from datetime import datetime
import pytz

# =========================
# 🔹 ВСТАВЬТЕ СВОЙ ТОКЕН
# =========================
TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"

# =========================
# 🔹 ВАШ TELEGRAM CHAT ID
# =========================
YOUR_CHAT_ID = 1008219132

# =========================
# Настройки
# =========================
STATS_FILE = "stats.txt"

app = Flask(__name__)


# =========================
# Функция обновления статистики
# =========================
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


# =========================
# Webhook
# =========================
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "OK"

    if "message" in data:

        # 📊 Статистика
        if "text" in data["message"] and data["message"]["text"].lower() == "статистика":

            try:
                with open(STATS_FILE, "r") as f:
                    stats = f.read().split(",")
                    joined = int(stats[0])
                    left = int(stats[1])
            except:
                joined = 0
                left = 0

            net = joined - left

            text = f"""📊 Статистика

➕ Пришло: {joined}
➖ Ушло: {left}
📈 Прирост: {net}
"""

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={
                    "chat_id": YOUR_CHAT_ID,
                    "text": text
                }
            )

        # 📥 Новый участник
        if "new_chat_members" in data["message"]:
            for user in data["message"]["new_chat_members"]:

                name = user.get("first_name", "Без имени")
                user_id = user.get("id")

                tz = pytz.timezone("Asia/Tashkent")
                time_now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

                text = (
                    "📥 Новый участник!\n\n"
                    f"👤 Имя: {name}\n"
                    f"🆔 ID: {user_id}\n"
                    f"⏰ Время: {time_now}"
                )

                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={
                        "chat_id": YOUR_CHAT_ID,
                        "text": text
                    }
                )

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

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={
                    "chat_id": YOUR_CHAT_ID,
                    "text": text
                }
            )

            update_stats(left=1)

    return "OK"


# =========================
# Главная страница
# =========================
@app.route("/")
def home():
    return "Bot is running"


# =========================
# Запуск
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
