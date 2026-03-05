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
# Файлы хранения
# =========================
DAILY_FILE = "daily_stats.txt"
MONTHLY_FILE = "monthly_stats.txt"
DATE_FILE = "current_date.txt"
MONTH_FILE = "current_month.txt"

app = Flask(__name__)

# =========================
# Получаем текущее время Ташкент
# =========================
def get_now():
    tz = pytz.timezone("Asia/Tashkent")
    return datetime.now(tz)

# =========================
# Проверка смены дня
# =========================
def check_day_reset():
    today = get_now().strftime("%Y-%m-%d")

    try:
        with open(DATE_FILE, "r") as f:
            saved_date = f.read().strip()
    except:
        saved_date = ""

    if saved_date != today:
        with open(DAILY_FILE, "w") as f:
            f.write("0,0")
        with open(DATE_FILE, "w") as f:
            f.write(today)

# =========================
# Проверка смены месяца
# =========================
def check_month_reset():
    current_month = get_now().strftime("%Y-%m")

    try:
        with open(MONTH_FILE, "r") as f:
            saved_month = f.read().strip()
    except:
        saved_month = ""

    if saved_month != current_month:
        with open(MONTHLY_FILE, "w") as f:
            f.write("0,0")
        with open(MONTH_FILE, "w") as f:
            f.write(current_month)

# =========================
# Обновление статистики
# =========================
def update_stats(file_name, joined=0, left=0):
    try:
        with open(file_name, "r") as f:
            data = f.read().split(",")
            current_joined = int(data[0])
            current_left = int(data[1])
    except:
        current_joined = 0
        current_left = 0

    current_joined += joined
    current_left += left

    with open(file_name, "w") as f:
        f.write(f"{current_joined},{current_left}")

# =========================
# Webhook
# =========================
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "OK"

    check_day_reset()
    check_month_reset()

    if "message" in data:

        message = data["message"]

        # 📊 Статистика дня
        if "text" in message and message["text"].lower() == "день":

            try:
                with open(DAILY_FILE, "r") as f:
                    stats = f.read().split(",")
                    joined = int(stats[0])
                    left = int(stats[1])
            except:
                joined = 0
                left = 0

            net = joined - left

            text = f"""📊 Статистика за сегодня

➕ Пришло: {joined}
➖ Ушло: {left}
📈 Прирост: {net}
"""

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": YOUR_CHAT_ID, "text": text}
            )

        # 📊 Статистика месяца
        if "text" in message and message["text"].lower() == "месяц":

            try:
                with open(MONTHLY_FILE, "r") as f:
                    stats = f.read().split(",")
                    joined = int(stats[0])
                    left = int(stats[1])
            except:
                joined = 0
                left = 0

            net = joined - left

            text = f"""📊 Статистика за месяц

➕ Пришло: {joined}
➖ Ушло: {left}
📈 Прирост: {net}
"""

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": YOUR_CHAT_ID, "text": text}
            )

        # 📥 Новый участник
        if "new_chat_members" in message:
            for user in message["new_chat_members"]:

                name = user.get("first_name", "Без имени")
                user_id = user.get("id")
                time_now = get_now().strftime("%Y-%m-%d %H:%M:%S")

                text = (
                    "📥 Новый участник!\n\n"
                    f"👤 Имя: {name}\n"
                    f"🆔 ID: {user_id}\n"
                    f"⏰ Время: {time_now}"
                )

                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={"chat_id": YOUR_CHAT_ID, "text": text}
                )

                update_stats(DAILY_FILE, joined=1)
                update_stats(MONTHLY_FILE, joined=1)

        # 📤 Участник вышел
        if "left_chat_member" in message:

            user = message["left_chat_member"]
            name = user.get("first_name", "Без имени")
            user_id = user.get("id")
            time_now = get_now().strftime("%Y-%m-%d %H:%M:%S")

            text = (
                "📤 Участник вышел!\n\n"
                f"👤 Имя: {name}\n"
                f"🆔 ID: {user_id}\n"
                f"⏰ Время: {time_now}"
            )

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": YOUR_CHAT_ID, "text": text}
            )

            update_stats(DAILY_FILE, left=1)
            update_stats(MONTHLY_FILE, left=1)

    return "OK"

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
