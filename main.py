import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# ۱. تنظیمات سرور برای رفع مشکل پورت در Render (پلن رایگان)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Roxana Bot is Live!")

    def log_message(self, format, *args):
        return # برای خلوت ماندن لاگ‌ها، پیام‌های سرور را چاپ نمی‌کنیم

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

# ۲. دریافت کلیدها از تنظیمات Render (بدون نمایش مستقیم در کد)
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ۳. پیکربندی هوش مصنوعی گوگل
genai.configure(api_key=GEMINI_KEY)

# --- تنظیمات هوشمند مدل ---
try:
    # پیدا کردن اولین مدل در دسترس که قابلیت تولید متن دارد
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models:
        selected_model_name = available_models[0] # معمولاً اولین مورد gemini-pro یا gemini-1.5-flash است
        print(f"✅ مدل انتخاب شده: {selected_model_name}")
        model = genai.GenerativeModel(selected_model_name)
    else:
        print("❌ هیچ مدلی پیدا نشد!")
        model = genai.GenerativeModel('gemini-pro') # مقدار پیش‌فرض
except Exception as e:
    print(f"⚠️ خطا در لیست کردن مدل‌ها: {e}")
    model = genai.GenerativeModel('gemini-pro')
# ------------------------

# ۴. تابع پردازش پیام‌های تلگرام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    print(f"Received message: {user_text}") # نمایش پیام در لاگ رندر

    try:
        # ارسال پیام به هوش مصنوعی با تعیین نقش
        prompt = f"تو مشاور هوشمند برند آرایشی و جواهرات رکسانا هستی. با لحنی محترمانه و صمیمی پاسخ بده: {user_text}"
        response = model.generate_content(prompt)
        
        await update.message.reply_text(response.text)
        print("Response sent successfully.")
        
    except Exception as e:
        print(f"Error in Gemini or Telegram: {e}")
        await update.message.reply_text("عذرخواهی می‌کنم، در حال حاضر ارتباط من با سیستم مرکزی قطع شده است. لطفاً کمی بعد دوباره تلاش کنید.")

# ۵. بخش اصلی اجرای برنامه
if __name__ == '__main__':
    print("Starting Roxana AI Bot...")
    
    if not TELEGRAM_TOKEN or not GEMINI_KEY:
        print("❌ ERROR: Environment variables (TOKEN/KEY) not found!")
    else:
        # الف: اجرای سرور سلامت در یک رشته (Thread) جداگانه
        threading.Thread(target=run_health_check_server, daemon=True).start()
        
        # ب: اجرای بات تلگرام
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is polling...")
        app.run_polling()
