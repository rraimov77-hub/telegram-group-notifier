import os
import requests
from flask import Flask, request
from datetime import datetime
import pytz

# =========================
# 🔹 ВСТАВЬТЕ СЮДА ТОКЕН
# =========================
TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"

# =========================
# 🔹 ВАШ TELEGRAM ID
# =========================
YOUR_CHAT_ID = 1008219132

app = Flask(__name__)

# =========================
# Время Ташкент
# =========================
def now_tashkent():
    tz = pytz.timezone("Asia/Tashkent")
    return datetime.now(tz)

# =========================
# Файлы по группе
# =========================
def daily_file(chat_id):
    return f"daily_{chat_id}.txt"

def monthly_file(chat_id):
    return f"monthly_{chat_id}.txt"

# =========================
# Обновление статистики
# =========================
def update_stats(file_name, joined=0, left=0):
    try:
        with open(file_name, "r") as f:
            data = f.read().split(",")
            j = int(data[0])
            l = int(data[1])
    except:
        j = 0
        l = 0

    j += joined
    l += left

    with open(file_name, "w") as f:
        f.write(f"{j},{l}")

# =========================
# Webhook
# =========================
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "OK"

    # =========================
    # Сообщения
    # =========================
    if "message" in data:

        message = data["message"]
        chat_id = message["chat"]["id"]
        chat_type = message["chat"]["type"]
        user_id = message["from"]["id"]

        # =========================
        # АДМИН-ПАНЕЛЬ (ТОЛЬКО ЛИЧКА)
        # =========================
        if message.get("text") == "/admin" and user_id == YOUR_CHAT_ID and chat_type == "private":

            keyboard = {
                "inline_keyboard": [
                    [{"text": "📊 Статистика дня", "callback_data": f"day_{chat_id}"}],
                    [{"text": "📈 Статистика месяца", "callback_data": f"month_{chat_id}"}]
                ]
            }

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": YOUR_CHAT_ID,
                    "text": "🔐 Админ-панель:",
                    "reply_markup": keyboard
                }
            )

            return "OK"

        # =========================
        # Новый участник
        # =========================
        if "new_chat_members" in message:
            for user in message["new_chat_members"]:

                name = user.get("first_name", "Без имени")
                time_now = now_tashkent().strftime("%Y-%m-%d %H:%M:%S")

                text = f"""📥 Новый участник

👤 Имя: {name}
⏰ Время: {time_now}
"""

                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={"chat_id": YOUR_CHAT_ID, "text": text}
                )

                update_stats(daily_file(chat_id), joined=1)
                update_stats(monthly_file(chat_id), joined=1)

        # =========================
        # Участник вышел
        # =========================
        if "left_chat_member" in message:

            user = message["left_chat_member"]
            name = user.get("first_name", "Без имени")
            time_now = now_tashkent().strftime("%Y-%m-%d %H:%M:%S")

            text = f"""📤 Участник вышел

👤 Имя: {name}
⏰ Время: {time_now}
"""

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": YOUR_CHAT_ID, "text": text}
            )

            update_stats(daily_file(chat_id), left=1)
            update_stats(monthly_file(chat_id), left=1)

    # =========================
    # Кнопки (callback)
    # =========================
    if "callback_query" in data:

        query = data["callback_query"]
        callback_data = query["data"]
        chat_id = int(callback_data.split("_")[1])

        if callback_data.startswith("day_"):

            try:
                with open(daily_file(chat_id), "r") as f:
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

        if callback_data.startswith("month_"):

            try:
                with open(monthly_file(chat_id), "r") as f:
                    stats = f.read().split(",")
                    joined = int(stats[0])
                    left = int(stats[1])
            except:
                joined = 0
                left = 0

            net = joined - left

            text = f"""📈 Статистика за месяц

➕ Пришло: {joined}
➖ Ушло: {left}
📊 Прирост: {net}
"""

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": YOUR_CHAT_ID, "text": text}
            )

    return "OK"


@app.route("/")
def home():
    return "Bot is running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
