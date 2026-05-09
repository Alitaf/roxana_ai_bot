import os
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. سرور سلامت برای رندر (Health Check)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Roxana is Online and Intelligent")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

# ۲. پیکربندی هوش مصنوعی و تلگرام
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

genai.configure(api_key=GEMINI_KEY)

# ۳. تابع اصلی پردازش پیام با مدل‌های اصلاح شده
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    print(f"User sent: {user_text}")

    # مدل‌ها با پیشوند دقیق models/ (حل مشکل خطای 404)
    model_names = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
    
    for name in model_names:
        try:
            print(f"Trying with: {name}")
            model = genai.GenerativeModel(name)
            # تعریف شخصیت رکسانا
            prompt = f"تو دستیار هوشمند 'رکسانا' هستی. با لحنی صمیمی و حرفه‌ای پاسخ بده: {user_text}"
            response = model.generate_content(prompt)
            
            if response and response.text:
                await update.message.reply_text(response.text)
                return 
        except Exception as e:
            print(f"Error with {name}: {e}")
            continue

    # اگر تمام مدل‌ها با خطا مواجه شدند
    await update.message.reply_text("عذرخواهی می‌کنم، سیستم هوش مصنوعی در حال حاضر پاسخگو نیست. لطفاً کمی بعد تلاش کنید.")

# ۴. نقطه شروع برنامه
if __name__ == '__main__':
    # اجرای سرور سلامت در پس‌زمینه
    threading.Thread(target=run_health_check, daemon=True).start()
    
    if not TELEGRAM_TOKEN or not GEMINI_KEY:
        print("Error: API Keys are missing in Environment Variables!")
    else:
        print("Starting Roxana Bot...")
        # استفاده از drop_pending_updates برای جلوگیری از تداخل (Conflict)
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is polling...")
        app.run_polling(drop_pending_updates=True)
