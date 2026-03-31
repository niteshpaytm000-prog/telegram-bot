import telebot

# 🔑 BOT DETAILS (baad me change kar lena)
BOT_TOKEN = "8639377241:AAEdDNLh6IwTDNJWyH8JWm1RXYP8WKePY1E"
BOT_USERNAME = "VIRTUAL_NUMBER74_BOT"

bot = telebot.TeleBot(BOT_TOKEN)

# ===== DATA =====
user_balance = {}
referrals = {}
users = set()

ADMIN_ID = 1292053214

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    users.add(user_id)

    if user_id not in user_balance:
        user_balance[user_id] = 0
        referrals[user_id] = 0

    # referral check
    if len(message.text.split()) > 1:
        ref_id = int(message.text.split()[1])
        if ref_id != user_id:
            referrals[ref_id] += 1

            if referrals[ref_id] >= 15:
                user_balance[ref_id] += 1
                referrals[ref_id] = 0

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Balance", "👥 Refer")
    markup.row("📲 Buy Number", "📢 Help")

    bot.send_message(
        message.chat.id,
        f"🔥 Welcome\n\n💰 Balance: {user_balance[user_id]}",
        reply_markup=markup
    )

# ===== BALANCE =====
@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def balance(message):
    user_id = message.chat.id
    bot.send_message(message.chat.id, f"💰 Your Balance: {user_balance.get(user_id,0)}")

# ===== REFER =====
@bot.message_handler(func=lambda m: m.text == "👥 Refer")
def refer(message):
    user_id = message.chat.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    bot.send_message(message.chat.id, f"👥 Share this link:\n{link}")

# ===== BUY =====
@bot.message_handler(func=lambda m: m.text == "📲 Buy Number")
def buy(message):
    bot.send_message(message.chat.id, "💳 Pay ₹10 and send 'paid'")

# ===== HELP =====
@bot.message_handler(func=lambda m: m.text == "📢 Help")
def help_msg(message):
    bot.send_message(message.chat.id, "Use buttons below 👇")

# ===== ADMIN ADD BALANCE =====
@bot.message_handler(commands=['addbal'])
def addbal(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        _, uid, amt = message.text.split()
        uid = int(uid)
        amt = int(amt)

        user_balance[uid] = user_balance.get(uid, 0) + amt
        bot.send_message(message.chat.id, "Balance added ✅")
    except:
        bot.send_message(message.chat.id, "Usage: /addbal user_id amount")

# ===== USERS =====
@bot.message_handler(commands=['users'])
def users_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, f"Total Users: {len(users)}")

# ===== BROADCAST =====
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id != ADMIN_ID:
        return

    msg = message.text.replace("/broadcast ", "")

    for user in users:
        try:
            bot.send_message(user, msg)
        except:
            pass

    bot.send_message(message.chat.id, "Broadcast sent ✅")

# ===== RUN =====
print("Bot running...")
bot.infinity_polling()
