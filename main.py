import os
import threading
from flask import Flask
import telebot

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- 1. Создаем веб-сервер, чтобы Render не усыплял бота ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_http():
    # Render передает порт через переменную PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. Логика твоего Telegram-бота ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот работает 24/7 абсолютно бесплатно!")

# --- 3. Запуск веб-сервера и бота ---
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    t = threading.Thread(target=run_http)
    t.start()
    
    # Запускаем постоянный опрос Telegram
    print("Бот запущен...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
