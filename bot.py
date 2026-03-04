import requests
from flask import Flask, request
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"
YOUR_CHAT_ID = 1008219132

app = Flask(__name__)

# Счётчики за день
stats = {
    "joined": 0,
    "left": 0
}

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:

        # Вход
        if "new_chat_members" in data["message"]:
            for user in data["message"]["new_chat_members"]:
                stats["joined"] += 1

        # Выход
        if "left_chat_member" in data["message"]:
            stats["left"] += 1

    return "OK"


def send_daily_report():
    joined = stats["joined"]
    left = stats["left"]
    net = joined - left

    text = f"""📊 Статистика за день

➕ Вошло: {joined}
➖ Вышло: {left}
📈 Чистый прирост: {net}
"""

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": YOUR_CHAT_ID,
        "text": text
    })

    # Сброс счётчиков
    stats["joined"] = 0
    stats["left"] = 0


# Планировщик
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, 'cron', hour=23, minute=0)
scheduler.start()


@app.route("/")
def home():
    return "Bot is running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
