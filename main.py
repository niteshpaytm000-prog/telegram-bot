import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pypdf import PdfReader, PdfWriter

TOKEN = "8778126599:AAHtdcyrqzbbgcB3LFTOr9_LhK4ioxQNuKw"
ADMIN_ID = 1292053214

user_files = {}
users = set()

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.message.chat_id)

    await update.message.reply_text(
        "🔥 Welcome to PDF Unlocker Bot\n\n📄 Send locked PDF\n🔐 Then send password"
    )

# PDF RECEIVE
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    path = f"{update.message.chat_id}.pdf"

    await file.download_to_drive(path)
    user_files[update.message.chat_id] = path

    await update.message.reply_text("🔐 Send password")

# PASSWORD
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
        await update.message.reply_text("✅ Done! PDF Unlocked")

    except:
        await update.message.reply_text("❌ Wrong password")

    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

        user_files.pop(chat_id, None)

# BROADCAST
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    msg = " ".join(context.args)

    for user in users:
        try:
            await context.bot.send_message(user, msg)
        except:
            pass

    await update.message.reply_text("✅ Broadcast Done")

# RUN BOT (IMPORTANT FIX 🔥)
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))

print("Bot Running 🚀")
app.run_polling()
