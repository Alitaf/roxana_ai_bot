import os, threading, google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. لیست محصولات سایت رکسانا (برای تست)
# می‌توانید نام، قیمت و لینک واقعی محصولات وردپرسی خود را اینجا وارد کنید
ROXANA_PRODUCTS = """
List of available products in Roxana Store:
1. Helen Seward Alchemy - for intensive nutri-hydration of lengths and ends - Price: 47,00 Dhs - Link: https://roxanacosmetic.com/product/alchemy-oil-30ml/?v=b6bb43df4525
2. Waterproof Volumizing Mascara - 24-hour durability - Price: 180,000 Tomans - Link: https://roxana.shop/product/mascara
3. 12-Color Eyeshadow Palette - Nude and Shine colors - Price: 320,000 Tomans - Link: https://roxana.shop/product/eyeshadow
4. Hyaluronic Acid Hydrating Serum - Skin rejuvenator - Price: 450,000 Tomans - Link: https://roxana.shop/product/serum
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
    
    # دستورالعمل هوشمند برای وفاداری به لیست و تشخیص خودکار زبان
    system_instruction = f"""
    You are 'Roxana', the EXCLUSIVE beauty consultant for Roxana Online Shop.
    
    STRICT RULES:
    1. ONLY use the product information provided in the list below. Do not invent products or suggest other brands.
    2. LANGUAGE MATCHING: Always respond in the SAME language that the user uses to ask their question (e.g., if they ask in English, answer in English; if in Persian, answer in Persian).
    3. If a product is NOT in the list, politely inform the user in their own language that we currently only offer the items available in our catalog.
    4. Always include the direct product link when mentioning a specific item.

    PRODUCT LIST:
    {ROXANA_PRODUCTS}
    
    Maintain a professional, helpful, and friendly tone in every language.
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
