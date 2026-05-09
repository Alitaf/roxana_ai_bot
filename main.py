import os
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. سرور سلامت برای رندر
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Roxana is Intelligent Now")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ۲. تنظیمات API
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
genai.configure(api_key=GEMINI_KEY)

# ۳. تابع پردازش هوشمند
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    try:
        # تلاش برای استفاده از مدل سریع
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"تو دستیار هوشمند 'رکسانا' هستی. خیلی صمیمی و حرفه‌ای پاسخ بده: {update.message.text}"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception:
        try:
            # اگر نشد، استفاده از مدل پایدار
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(update.message.text)
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text("سیستم هوش مصنوعی موقتاً در دسترس نیست، اما من (رکسانا) آنلاین هستم!")

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    # استفاده از drop_pending_updates برای جلوگیری از Conflict دوباره
    app.run_polling(drop_pending_updates=True)
