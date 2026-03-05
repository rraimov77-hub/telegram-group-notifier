import os
import requests
from flask import Flask, request
from datetime import datetime
import pytz

# =========================
# 🔹 ВСТАВЬТЕ СЮДА СВОЙ ТОКЕН
# =========================
TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"

# =========================
# 🔹 ВАШ CHAT ID (куда приходят уведомления)
# =========================
YOUR_CHAT_ID = 1008219132

app = Flask(__name__)

# =========================
# Время Ташкент
# =========================
def get_now():
    tz = pytz.timezone("Asia/Tashkent")
    return datetime.now(tz)

# =========================
# Файлы по группе
# =========================
def get_daily_file(chat_id):
    return f"daily_{chat_id}.txt"

def get_monthly_file(chat_id):
    return f"monthly_{chat_id}.txt"

def get_date_file(chat_id):
    return f"date_{chat_id}.txt"

def get_month_file(chat_id):
    return f"month_{chat_id}.txt"

# =========================
# Авто-сброс дня
# =========================
def check_day_reset(chat_id):
    today = get_now().strftime("%Y-%m-%d")
    file_name = get_date_file(chat_id)

    try:
        with open(file_name, "r") as f:
            saved = f.read().strip()
    except:
        saved = ""

    if saved != today:
        with open(get_daily_file(chat_id), "w") as f:
            f.write("0,0")
        with open(file_name, "w") as f:
            f.write(today)

# =========================
# Авто-сброс месяца
# =========================
def check_month_reset(chat_id):
    current_month = get_now().strftime("%Y-%m")
    file_name = get_month_file(chat_id)

    try:
        with open(file_name, "r") as f:
            saved = f.read().strip()
    except:
        saved = ""

    if saved != current_month:
        with open(get_monthly_file(chat_id), "w") as f:
            f.write("0,0")
        with open(file_name, "w") as f:
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

    if "message" in data:

        message = data["message"]
        chat_id = message["chat"]["id"]

        check_day_reset(chat_id)
        check_month_reset(chat_id)

        # 📊 Статистика дня
        if "text" in message and message["text"].lower() == "день":

            try:
                with open(get_daily_file(chat_id), "r") as f:
                    stats = f.read().split(",")
                    joined = int(stats[0])
                    left = int(stats[1])
            except:
                joined = 0
                left = 0

            net = joined - left

            text = f"""📊 Статистика за день

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
                with open(get_monthly_file(chat_id), "r") as f:
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

                update_stats(get_daily_file(chat_id), joined=1)
                update_stats(get_monthly_file(chat_id), joined=1)

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

            update_stats(get_daily_file(chat_id), left=1)
            update_stats(get_monthly_file(chat_id), left=1)

    return "OK"


@app.route("/")
def home():
    return "Bot is running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
