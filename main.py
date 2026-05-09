import os, threading, google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. لیست محصولات سایت رکسانا (برای تست)
# می‌توانید نام، قیمت و لینک واقعی محصولات وردپرسی خود را اینجا وارد کنید
ROXANA_PRODUCTS = """
لیست محصولات موجود در فروشگاه رکسانا:
1. کرم پودر مات رکسانا - مناسب پوست‌های چرب - قیمت: ۲۵۰,۰۰۰ تومان - لینک: https://roxana.shop/product/foundation
2. ریمل حجم‌دهنده ضدآب - ماندگاری ۲۴ ساعته - قیمت: ۱۸۰,۰۰۰ تومان - لینک: https://roxana.shop/product/mascara
3. پالت سایه چشم ۱۲ رنگ - رنگ‌های نود و شاین - قیمت: ۳۲۰,۰۰۰ تومان - لینک: https://roxana.shop/product/eyeshadow
4. سرم آبرسان هیالورونیک اسید - جوانساز پوست - قیمت: ۴۵۰,۰۰۰ تومان - لینک: https://roxana.shop/product/serum
"""

# ۲. سرور سلامت برای رندر
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Roxana Shop Bot is Active")

def run_health_check():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), HealthCheckHandler)
    server.serve_forever()

# ۳. تنظیمات Gemini
genai.configure(api_key=os.getenv("GEMINI_KEY"))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_text = update.message.text
    
    # مدل‌هایی که در لیست مجاز شما بودند
    target_models = ['models/gemini-3.1-flash-lite', 'models/gemini-2.0-flash']
    
    # ساخت پرامپت هوشمند: ترکیب شخصیت رکسانا با اطلاعات محصولات
    system_instruction = f"""
    تو 'رکسانا' هستی، مشاور تخصصی فروشگاه لوازم آرایشی رکسانا. 
    وظیفه تو راهنمایی مشتریان است. اگر کاربر درباره محصولی سوال کرد که در لیست زیر وجود دارد، 
    حتماً آن را پیشنهاد بده و لینک خریدش را هم بفرست. 
    اگر محصول در لیست نبود، با ادب بگو که فعلاً موجود نداریم ولی می‌توانیم راهنمایی‌شان کنیم.
    
    اطلاعات محصولات ما:
    {ROXANA_PRODUCTS}
    
    پاسخ کاربر را به فارسی صمیمی و حرفه‌ای بده.
    """

    for model_name in target_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(f"{system_instruction}\n\nسوال کاربر: {user_text}")
            
            if response and response.text:
                await update.message.reply_text(response.text)
                return 
        except Exception:
            continue

    await update.message.reply_text("🔴 مشکلی در پردازش پیش آمد، لطفاً دوباره بپرسید.")

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
