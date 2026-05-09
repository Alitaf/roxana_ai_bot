import os, threading, google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. سرور سلامت برای رندر
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Roxana v3.1 is Active")

def run_health_check():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), HealthCheckHandler)
    server.serve_forever()

# ۲. تنظیمات
genai.configure(api_key=os.getenv("GEMINI_KEY"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ۳. پردازشگر با مدل‌های لیست اختصاصی شما
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    # استفاده از مدل‌هایی که خود گوگل تایید کرده (models/gemini-3.1-flash-lite و غیره)
    target_models = [
        'models/gemini-3.1-flash-lite', 
        'models/gemini-2.5-flash',
        'models/gemini-2.0-flash'
    ]
    
    for model_name in target_models:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"تو 'رکسانا' هستی، یک دستیار هوشمند و صمیمی. پاسخ بده: {update.message.text}"
            response = model.generate_content(prompt)
            
            if response and response.text:
                await update.message.reply_text(response.text)
                return 
        except Exception:
            continue

    await update.message.reply_text("🔴 خطا در اتصال به مدل‌های جدید. لطفاً لحظاتی دیگر تلاش کنید.")

# ۴. اجرا
if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
