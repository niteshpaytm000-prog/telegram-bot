import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pypdf import PdfReader, PdfWriter

# 🔑 BOT CONFIG
TOKEN = "8778126599:AAHtdcyrqzbbgcB3LFTOr9_LhK4ioxQNuKw"
ADMIN_ID = 1292053214  # ✅ tera admin ID set

# storage
user_files = {}
users = set()

# 🔥 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    users.add(user_id)

    welcome_text = """
🔥 *Welcome to PDF Unlocker Bot* 🔥

📄 Send me any *locked PDF file*
🔐 Then send password
⚡ I will unlock it instantly

💡 Fast | Secure | Easy to use
"""

    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# 📄 HANDLE PDF
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"{update.message.chat_id}.pdf"

    await file.download_to_drive(file_path)

    user_files[update.message.chat_id] = file_path

    await update.message.reply_text("🔐 Please send password to unlock this PDF")

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

        # 📤 send file
        await update.message.reply_document(document=open(output_file, "rb"))

        # 🎉 success message
        success_msg = """
✅ *PDF Successfully Unlocked!*

📂 Your file is ready above 👆

⭐ Share this bot with friends!
🚀 More features coming soon...
"""
        await update.message.reply_text(success_msg, parse_mode="Markdown")

    except:
        await update.message.reply_text("❌ Wrong password or error occurred")

    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

        user_files.pop(chat_id, None)

# 📢 ADMIN BROADCAST
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not admin")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /broadcast message")
        return

    msg = " ".join(context.args)

    sent = 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=user, text=msg)
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {sent} users")

# 🚀 MAIN
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))

    print("Bot Running 🚀")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
