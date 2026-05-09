import os, threading, google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

def run_health():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), BaseHTTPRequestHandler)
    server.serve_forever()

genai.configure(api_key=os.getenv("GEMINI_KEY"))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    
    # لیست تمام نام‌های ممکن برای مدل که گوگل ممکن است بپذیرد
    possible_models = [
        'gemini-1.5-flash', 
        'models/gemini-1.5-flash', 
        'gemini-pro', 
        'models/gemini-pro'
    ]
    
    for model_name in possible_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(update.message.text)
            if response and response.text:
                await update.message.reply_text(response.text)
                return # به محض اینکه یکی جواب داد، خارج شو
        except Exception as e:
            print(f"تلاش با {model_name} شکست خورد.")
            continue # برو سراغ نام بعدی مدل

    await update.message.reply_text("🔴 متاسفانه گوگل در این لحظه پاسخگو نیست. لطفاً چند لحظه دیگر پیام دهید.")

if __name__ == '__main__':
    threading.Thread(target=run_health, daemon=True).start()
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT, handle))
    app.run_polling(drop_pending_updates=True)
