import os
import requests
from flask import Flask, request
from datetime import datetime
import pytz

# ======================
# 🔹 ВСТАВЬ СЮДА ТОКЕН
# ======================
TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"

# ======================
# 🔹 ВСТАВЬ СЮДА СВОЙ TELEGRAM ID
# ======================
YOUR_CHAT_ID = 1008219132
# ======================
# ФАЙЛЫ
# ======================
GROUPS_FILE = "groups.txt"

app = Flask(__name__)


# ======================
# СОХРАНЕНИЕ ГРУПП
# ======================
def save_group(chat_id, title):
    try:
        with open(GROUPS_FILE, "r") as f:
            groups = f.read().splitlines()
    except:
        groups = []

    for g in groups:
        if str(chat_id) in g:
            return

    with open(GROUPS_FILE, "a") as f:
        f.write(f"{chat_id}|{title}\n")


# ======================
# WEBHOOK
# ======================
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "OK"

    # ======================
    # ОБРАБОТКА СООБЩЕНИЙ
    # ======================
    if "message" in data:

        message = data["message"]
        chat = message["chat"]
        chat_id = chat["id"]
        chat_title = chat.get("title", "Личная переписка")
        user_id = message["from"]["id"]

        # Сохраняем группы
        if chat["type"] in ["group", "supergroup"]:
            save_group(chat_id, chat_title)

        # ======================
        # АДМИН ПАНЕЛЬ
        # ======================
        if message.get("text") == "/admin" and user_id == YOUR_CHAT_ID:

            try:
                with open(GROUPS_FILE, "r") as f:
                    groups = f.read().splitlines()
            except:
                groups = []

            keyboard_buttons = []

            for g in groups:
                chat_id_saved, title = g.split("|")
                keyboard_buttons.append([
                    {"text": f"📊 {title}", "callback_data": f"group_{chat_id_saved}"}
                ])

            keyboard = {"inline_keyboard": keyboard_buttons}

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": YOUR_CHAT_ID,
                    "text": "🔐 Админ-панель",
                    "reply_markup": keyboard
                }
            )

        # ======================
        # ВХОД УЧАСТНИКА
        # ======================
        if "new_chat_members" in message:
            for _ in message["new_chat_members"]:
                update_stats(chat_id, joined=1)

        # ======================
        # ВЫХОД УЧАСТНИКА
        # ======================
        if "left_chat_member" in message:
            update_stats(chat_id, left=1)

    # ======================
    # ОБРАБОТКА КНОПОК
    # ======================
    if "callback_query" in data:

        callback_data = data["callback_query"]["data"]

        if callback_data.startswith("group_"):

            chat_id = callback_data.split("_")[1]
            file_name = f"stats_{chat_id}.txt"

            try:
                with open(file_name, "r") as f:
                    stats = f.read().split(",")
                    joined = int(stats[0])
                    left = int(stats[1])
            except:
                joined = 0
                left = 0

            net = joined - left
            net_text = f"+{net}" if net > 0 else str(net)

            text = f"""📊 ОТЧЁТ ПО ГРУППЕ

🏷 ID группы: {chat_id}

➕ Пришло: {joined}
➖ Ушло: {left}
📈 Чистый прирост: {net_text}
"""

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={
                    "chat_id": YOUR_CHAT_ID,
                    "text": text
                }
            )

    return "OK"


# ======================
# СТАТИСТИКА
# ======================
def update_stats(chat_id, joined=0, left=0):
    file_name = f"stats_{chat_id}.txt"

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


# ======================
# HOME
# ======================
@app.route("/")
def home():
    return "Bot is running"


# ======================
# ЗАПУСК
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
