import os, threading, google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

def run_health():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), BaseHTTPRequestHandler)
    server.serve_forever()

genai.configure(api_key=os.getenv("GEMINI_KEY"))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    # استفاده از مدل پایدار و تست شده
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-8b') # این نسخه سبک‌تر و بسیار پایدارتر است
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        # اگر باز هم خطا داد، دقیقاً مدل‌های در دسترس کلید شما را چاپ می‌کند
        try:
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            await update.message.reply_text(f"گوگل لجبازی می‌کند. مدل‌های مجاز شما: {available}")
        except:
            await update.message.reply_text(f"خطای نهایی: {str(e)[:100]}")

if __name__ == '__main__':
    threading.Thread(target=run_health, daemon=True).start()
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT, handle))
    app.run_polling(drop_pending_updates=True)
