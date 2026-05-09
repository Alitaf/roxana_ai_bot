import os, threading, google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. سرور سلامت برای رندر
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Roxana v3.1 is Online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ۲. تنظیمات API
genai.configure(api_key=os.getenv("GEMINI_KEY"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ۳. پردازشگر هوشمند بر اساس لیست مدل‌های اختصاصی شما
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    # استفاده از دقیق‌ترین نام‌ها از لیست مجاز شما (May 2026)
    target_models = [
        'models/gemini-2.0-flash', 
        'models/gemini-3.1-flash-lite', 
        'models/gemini-flash-latest'
    ]
    
    for model_name in target_models:
        try:
            model = genai.GenerativeModel(model_name)
            # تعریف شخصیت برای رکسانا
            prompt = f"تو 'رکسانا' هستی، یک دستیار هوشمند، صمیمی و بسیار حرفه‌ای. پاسخ بده: {update.message.text}"
            response = model.generate_content(prompt)
            
            if response and response.text:
                await update.message.reply_text(response.text)
                return 
        except Exception as e:
            print(f"تلاش با {model_name} ناموفق بود: {e}")
            continue

    await update.message.reply_text("🔴 متاسفانه مدل‌های جدید گوگل هنوز در ریجن شما فعال نشده‌اند. لحظاتی دیگر تلاش کنید.")

# ۴. اجرای برنامه
if __name__ == '__main__':
    # بیدار نگه داشتن پورت رندر
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # راه‌اندازی تلگرام
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # پاکسازی آپدیت‌های معلق برای جلوگیری از Conflict
    app.run_polling(drop_pending_updates=True)
