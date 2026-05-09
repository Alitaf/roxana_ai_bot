import os, threading, google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# سرور سلامت برای رندر
def run_health():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), BaseHTTPRequestHandler)
    server.serve_forever()

# تنظیمات
genai.configure(api_key=os.getenv("GEMINI_KEY"))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    try:
        # تست مستقیم با آخرین مدل گوگل
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        # اینجا دقیقاً می‌فهمیم مشکل گوگل چیست
        await update.message.reply_text(f"🔴 خطای واقعی: {str(e)[:200]}")

if __name__ == '__main__':
    threading.Thread(target=run_health, daemon=True).start()
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT, handle))
    app.run_polling(drop_pending_updates=True)
