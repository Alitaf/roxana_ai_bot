import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"رکسانا آنلاین است! شما گفتید: {update.message.text}")

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT, echo))
    # خط آخر را به این شکل تغییر دهید:
app.run_polling(drop_pending_updates=True)
