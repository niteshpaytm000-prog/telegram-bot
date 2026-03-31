import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pypdf import PdfReader, PdfWriter

# 🔑 CONFIG
TOKEN = "8778126599:AAHtdcyrqzbbgcB3LFTOr9_LhK4ioxQNuKw"
ADMIN_ID = 1292053214

user_files = {}
users = set()

# 🔥 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    users.add(user_id)

    text = """
🔥 *Welcome to PDF Unlocker Bot* 🔥

📄 Send locked PDF
🔐 Then send password
⚡ Get unlocked file instantly

💡 Fast | Secure | Easy
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# 📄 HANDLE PDF
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    path = f"{update.message.chat_id}.pdf"

    await file.download_to_drive(path)
    user_files[update.message.chat_id] = path

    await update.message.reply_text("🔐 Send password to unlock PDF")

# 🔐 HANDLE PASSWORD
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if chat_id not in user_files:
        return

    password = update.message.text
    input_file = user_files[chat_id]
    output_file = f"{chat_id}_unlocked.pdf"

    try:
        reader = PdfReader(input_file)

        if reader.is_encrypted:
            reader.decrypt(password)

        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        with open(output_file, "wb") as f:
            writer.write(f)

        await update.message.reply_document(open(output_file, "rb"))

        await update.message.reply_text(
            "✅ PDF Unlocked Successfully!\n\n⭐ Share this bot with friends 🚀"
        )

    except:
        await update.message.reply_text("❌ Wrong password or error")

    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

        user_files.pop(chat_id, None)

# 📢 BROADCAST
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        await update.message.reply_text("❌ Not allowed")
        return

    if not context.args:
        await update.message.reply_text("❌ Use: /broadcast message")
        return

    msg = " ".join(context.args)

    count = 0
    for user in users:
        try:
            await context.bot.send_message(user, msg)
            count += 1
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {count} users")

# 🚀 MAIN
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))

    print("Bot Running 🚀")
    await app.run_polling()

# 🔥 FIXED RUN (NO CRASH)
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
