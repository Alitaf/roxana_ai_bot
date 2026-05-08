import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# خواندن کلیدها از تنظیمات مخفی سرور
GEMINI_KEY = os.getenv("AIzaSyAnQwmKRqSdoMbW6OOQgAMlOLMbpxgYswE")
TELEGRAM_TOKEN = os.getenv("8687901520:AAHqsvH90wemum3_evMykNzmb9eFRC17mVs")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # دانش محصولات رکسانا را اینجا هم می‌توانی اضافه کنی
    response = model.generate_content(f"تو مشاور رکسانا هستی: {user_text}")
    await update.message.reply_text(response.text)

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
