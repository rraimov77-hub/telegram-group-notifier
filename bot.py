import os
import requests
from flask import Flask, request
from datetime import datetime
import pytz

# =========================
# 🔐 ВСТАВЬТЕ СВОЙ ТОКЕН
# =========================
TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"

# =========================
# 🔐 ВАШ TELEGRAM ID
# =========================
YOUR_CHAT_ID = 1008219132

app = Flask(__name__)

GROUPS_FILE = "groups.txt"

# =========================
# Время Ташкент
# =========================
def now():
    tz = pytz.timezone("Asia/Tashkent")
    return datetime.now(tz)

# =========================
# Сохранение групп
# =========================
def save_group(chat_id, title):
    try:
        with open(GROUPS_FILE, "r") as f:
            groups = f.read().splitlines()
    except:
        groups = []

    entry = f"{chat_id}|{title}"

    if entry not in groups:
        groups.append(entry)
        with open(GROUPS_FILE, "w") as f:
            f.write("\n".join(groups))

# =========================
# Файлы статистики
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
# WEBHOOK
# =========================
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "OK"

    # =====================
    # CALLBACK КНОПКИ
    # =====================
    if "callback_query" in data:
        query = data["callback_query"]
        callback_data = query["data"]

        if callback_data == "day":
            text = "📊 Дневная статистика обновляется автоматически по группам."
        elif callback_data == "month":
            text = "📈 Месячная статистика обновляется автоматически по группам."
        else:
            text = "OK"

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": YOUR_CHAT_ID, "text": text}
        )

        return "OK"

    # =====================
    # СООБЩЕНИЯ
    # =====================
    if "message" in data:

        message = data["message"]
        chat_id = message["chat"]["id"]
        chat_type = message["chat"]["type"]
        user_id = message["from"]["id"]

        # Сохраняем группу
        chat_title = message["chat"].get("title", "Личная переписка")
        save_group(chat_id, chat_title)

        # Админ-панель
        if message.get("text") == "/admin" and user_id == YOUR_CHAT_ID and chat_type == "private":

            groups_text = "📋 Список групп:\n\n"

            try:
                with open(GROUPS_FILE, "r") as f:
                    groups = f.read().splitlines()
            except:
                groups = []

            if not groups:
                groups_text += "Группы пока не найдены."
            else:
                for g in groups:
                    gid, title = g.split("|")
                    groups_text += f"• {title}\n"

            keyboard = {
                "inline_keyboard": [
                    [{"text": "📊 Статистика", "callback_data": "day"}]
                ]
            }

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": YOUR_CHAT_ID,
                    "text": "🔐 Админ-панель\n\n" + groups_text,
                    "reply_markup": keyboard
                }
            )

            return "OK"

        # Новый участник
        if "new_chat_members" in message:
            for user in message["new_chat_members"]:

                name = user.get("first_name", "Без имени")
                time_now = now().strftime("%Y-%m-%d %H:%M:%S")

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

        # Участник вышел
        if "left_chat_member" in message:

            user = message["left_chat_member"]
            name = user.get("first_name", "Без имени")
            time_now = now().strftime("%Y-%m-%d %H:%M:%S")

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

    return "OK"


@app.route("/")
def home():
    return "Bot is running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
