import os
import sqlite3
import threading
from flask import Flask
import telebot
from openai import OpenAI

# ==========================================
# 1. RENDER UCHUN FLASK VEB-SERVERI
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Yo'l-yo'lakay boti aktiv va ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Veb-serverni fonda (background thread) ishga tushirish
threading.Thread(target=run_flask, daemon=True).start()

# ==========================================
# 2. BOT VA DEEPSEEK SOZLAMALARI
# ==========================================
# Telegram Bot Token va DeepSeek API Kalitlari
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8745929395:AAGtESjD0aXGYMQ4EBjqiXZUOMC4BQPUaRA")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-3db2b2e3e58f4b62a65f49beee697bed")

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ==========================================
# 3. SQLITE MA'LUMOTLAR BAZASI
# ==========================================
def init_db():
    conn = sqlite3.connect("yol_yolakar.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            role TEXT,
            phone TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 4. TELEGRAM BOT BUYRUQLARI VA AILOGIKA
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Assalomu alaykum! 'Yo‘l-yo‘lakay' logistika botiga xush kelibsiz! 🚛\n\n"
        "Men sizga yuk va yo'lovchi tashish bo'yicha yordam beruvchi AI yordamchisiman.\n"
        "Qanday yordam bera olaman?"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    user_text = message.text
    
    # Foydalanuvchiga javob tayyorlanayotgani haqida habar berish
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # DeepSeek AI modeliga so'rov yuborish
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Siz Uzbekistan bo'ylab 'Yo'l-yo'lakay' mikro-logistika boti AI yordamchisisiz. Foydalanuvchilarga xushmuomala va o'zbek tilida aniq javob bering."},
                {"role": "user", "content": user_text}
            ],
            stream=False
        )
        ai_reply = response.choices[0].message.content
        bot.reply_to(message, ai_reply)
    except Exception as e:
        bot.reply_to(message, "Kechirasiz, javob tayyorlashda xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring.")

# ==========================================
# 5. BOTNI ISHGA TUSHIRISH
# ==========================================
if __name__ == "__main__":
    print("Yo'l-yo'lakay boti ishga tushdi...")
    bot.infinity_polling()

