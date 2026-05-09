import os, threading, google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ۱. لیست محصولات سایت رکسانا (برای تست)
# می‌توانید نام، قیمت و لینک واقعی محصولات وردپرسی خود را اینجا وارد کنید
ROXANA_PRODUCTS = """
List of available products in Roxana Store:
1. Helen Seward Alchemy - for intensive nutri-hydration of lengths and ends - Price: 47.00 Dhs - Link: https://roxanacosmetic.com/product/alchemy-oil-30ml/?v=b6bb43df4525
2. Helen Seward Crystal Wax - Modeling wax with a glossy effect gives extreme definition and shine. - Price: 78.00 Dhs - Link: https://roxanacosmetic.com/product/crystal-wax-100-ml/?v=b6bb43df4525
3. Helen Seward Hydra Conditioner - Conditioner for colored and treated hair - Price: 54.00 Dhs - Link: https://roxanacosmetic.com/product/hydra-conditioner-300ml/?v=b6bb43df4525
4. Helen Seward Hydra Shampoo - Shampoo for colored and damaged hair - Price: 49.00 Dhs - Link: https://roxanacosmetic.com/product/hydra-shampoo-300ml/?v=b6bb43df4525
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
