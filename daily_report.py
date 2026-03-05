import requests
import os

TOKEN = os.environ.get("8554074737:AAGTnrbU6kfm0rxGxxs1rTq5waaZIlN3lbE")
YOUR_CHAT_ID = 1008219132

# Читаем файл со статистикой
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

# Сбрасываем статистику
with open("stats.txt", "w") as f:
    f.write("0,0")
