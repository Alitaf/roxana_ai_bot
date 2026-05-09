import os
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. سرور سلامت برای رندر (جلوگیری از خطای پورت)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Roxana Bot is Online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

# ۲. پیکربندی هوش مصنوعی و تلگرام
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

genai.configure(api_key=GEMINI_KEY)

# ۳. تابع اصلی پردازش پیام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    print(f"پیام دریافتی: {user_text}")

    # لیست اولویت‌بندی شده مدل‌ها برای اطمینان از پاسخگویی
    model_names = ['gemini-1.5-flash', 'gemini-pro']
    
    for name in model_names:
        try:
            print(f"در حال تلاش با مدل: {name}")
            model = genai.GenerativeModel(name)
            # ایجاد یک پرومپت شخصیتی برای رکسانا
            prompt = f"تو دستیار هوشمند 'رکسانا' هستی. با لحنی محترمانه و صمیمی پاسخ بده: {user_text}"
            response = model.generate_content(prompt)
            
            if response and response.text:
                await update.message.reply_text(response.text)
                return  # خروج از حلقه در صورت موفقیت
        except Exception as e:
            print(f"خطا در مدل {name}: {e}")
            continue

    # اگر هیچ مدلی پاسخ نداد
    await update.message.reply_text("عذرخواهی می‌کنم، ارتباط من با مرکز کمی کُند است. لطفاً دوباره پیام دهید.")

# ۴. نقطه شروع برنامه
if __name__ == '__main__':
    # اجرای سرور سلامت در یک ترد جداگانه
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # راه‌اندازی بات تلگرام
    if not TELEGRAM_TOKEN:
        print("خطا: TELEGRAM_TOKEN تنظیم نشده است!")
    else:
        print("بات در حال راه‌اندازی...")
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # هندلر برای پیام‌های متنی
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        # شروع به کار بات
        app.run_polling()
