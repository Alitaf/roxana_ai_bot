import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. سرور سلامت برای رندر (Port Binding)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ۲. پیکربندی APIها
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
genai.configure(api_key=GEMINI_KEY)

# ۳. استفاده از نام عمومی مدل برای سازگاری حداکثری
model = genai.GenerativeModel('gemini-1.5-flash')

# ۴. تابع پردازش پیام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        # استفاده از مدل به صورت مستقیم
        response = model.generate_content(f"تو دستیار رکسانا هستی: {update.message.text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        # اگر دوباره خطا داد، با مدل جایگزین تست کن
        try:
            alt_model = genai.GenerativeModel('gemini-pro')
            response = alt_model.generate_content(update.message.text)
            await update.message.reply_text(response.text)
        except:
            await update.message.reply_text("در حال به‌روزرسانی سیستم هستم، لطفاً لحظاتی دیگر پیام دهید.")

if __name__ == '__main__':
    # اجرای سرور سلامت در پس‌زمینه
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # اجرای بات تلگرام
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
