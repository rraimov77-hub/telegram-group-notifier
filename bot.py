import requests
from flask import Flask, request

TOKEN = "8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE"
YOUR_CHAT_ID = 1008219132

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        if "new_chat_members" in data["message"]:
            for user in data["message"]["new_chat_members"]:
                name = user.get("first_name", "Новый участник")

                text = f"Новый участник в группе: {name}"

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
