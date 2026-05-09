import os, threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. سرور سلامت برای رندر
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Roxana is Online")

def run_health_check():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), HealthCheckHandler)
    server.serve_forever()

# ۲. تنظیمات
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
genai.configure(api_key=GEMINI_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    try:
        # استراتژی جدید: پیدا کردن اولین مدل در دسترس به صورت خودکار
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            await update.message.reply_text("گوگل هیچ مدلی را برای این کلید مجاز نمی‌داند.")
            return

        # استفاده از اولین مدل موجود (مثلاً gemini-1.5-flash)
        model = genai.GenerativeModel(available_models[0])
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
        
    except Exception as e:
        # نمایش خطای واقعی برای حل نهایی
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg:
            await update.message.reply_text("خطا: کلید API معتبر نیست. لطفاً در تنظیمات رندر چک کنید.")
        else:
            await update.message.reply_text(f"خطای سیستم: {error_msg[:100]}")

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
