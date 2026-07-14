import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import sqlite3
import json

TOKEN = "8908913545:AAFqVtBWMZNTrJQKGJxDPyi3wsSHC9iv77Y"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8455479648

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, username TEXT, balance REAL)''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start(m):
    user_id = m.from_user.id
    username = m.from_user.username or "User"
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, balance) VALUES (?, ?, ?)", (user_id, username, 100.0))
    if user_id == ADMIN_ID:
        cursor.execute("UPDATE users SET balance = 999999999.0 WHERE user_id = ?", (user_id,))
    conn.commit()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    balance = float(result) if result else 0.0
    conn.close()

    text = (
        f"Welcome! You have entered my crypto bot.\n\n"
        f"💰 Ваш баланс: {balance:,.2f} USD\n\n"
        f" В меню встроен кошелек, P2P Маркет и Crash-Казино (Ракетка)!"
    )
    
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    # Используем чистый веб-хостинг
    web_app_url = "https://github.io" 
    kb.add(KeyboardButton("🚀 Открыть Кошелек & Казино", web_app=WebAppInfo(url=web_app_url)))
    bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(content_types=['web_app_data'])
def web_app_data_handler(m):
    try:
        data = json.loads(m.web_app_data.data)
        action = data.get("action")
        user_id = m.from_user.id
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        if action == "casino_result":
            bet = float(data.get("bet"))
            profit = float(data.get("profit"))
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            res = cursor.fetchone()
            current_balance = float(res) if res else 0.0
            
            if profit > 0:
                new_balance = current_balance + (profit - bet) if user_id != ADMIN_ID else current_balance
                if user_id != ADMIN_ID:
                    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
                bot.send_message(m.chat.id, f"🚀 **Ракета долетела!**\n💰 Выигрыш: +{profit} USD")
            else:
                new_balance = current_balance - bet if user_id != ADMIN_ID else current_balance
                if user_id != ADMIN_ID:
                    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
                bot.send_message(m.chat.id, f"💥 **Ракета взорвалась!**\nВы потеряли ставку: -{bet} USD")
            conn.commit()
        conn.close()
    except Exception as e:
        bot.send_message(m.chat.id, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
