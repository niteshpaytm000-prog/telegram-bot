from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

ADMIN_ID = 1292053214
BOT_TOKEN = "8639377241:AAEdDNLh6IwTDNJWyH8JWm1RXYP8WKePY1E"
BOT_USERNAME = "VIRTUAL_NUMBER74_BOT"

USERS_FILE = "users.txt"
BAL_FILE = "balance.txt"
REF_FILE = "ref.txt"

# ===== LOAD/SAVE =====
def load_data(file):
    if not os.path.exists(file):
        return {}
    data = {}
    with open(file, "r") as f:
        for line in f:
            k, v = line.strip().split(":")
            data[int(k)] = int(v)
    return data

def save_data(file, data):
    with open(file, "w") as f:
        for k, v in data.items():
            f.write(f"{k}:{v}\n")

users = set()
balance = load_data(BAL_FILE)
referrals = load_data(REF_FILE)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    users.add(user_id)
    if user_id not in balance:
        balance[user_id] = 0
        referrals[user_id] = 0
        save_data(BAL_FILE, balance)
        save_data(REF_FILE, referrals)

    # referral handle
    if context.args:
        ref_id = int(context.args[0])
        if ref_id != user_id:
            referrals[ref_id] += 1
            if referrals[ref_id] >= 15:
                balance[ref_id] += 1
                referrals[ref_id] = 0

            save_data(REF_FILE, referrals)
            save_data(BAL_FILE, balance)

    await update.message.reply_text(
        f"🔥 Welcome\n\n💰 Balance: {balance[user_id]}"
    )

# ===== BALANCE =====
async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(f"💰 Balance: {balance.get(user_id,0)}")

# ===== REFER =====
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"Invite link:\n{link}")

# ===== BUY =====
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Pay ₹10\nSend 'paid' after payment")

# ===== ADMIN ADD BAL =====
async def addbal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    amount = int(context.args[1])

    balance[user_id] = balance.get(user_id, 0) + amount
    save_data(BAL_FILE, balance)

    await update.message.reply_text("Balance added ✅")

# ===== USERS =====
async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    await update.message.reply_text(f"Total Users: {len(users)}")

# ===== BROADCAST =====
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    msg = " ".join(context.args)

    for user in users:
        try:
            await context.bot.send_message(chat_id=user, text=msg)
        except:
            pass

    await update.message.reply_text("Broadcast sent ✅")

# ===== APP =====
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", bal))
app.add_handler(CommandHandler("refer", refer))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("addbal", addbal))
app.add_handler(CommandHandler("users", users_cmd))
app.add_handler(CommandHandler("broadcast", broadcast))

print("Bot running...")
app.run_polling()
