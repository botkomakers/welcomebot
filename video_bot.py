import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from flask import Flask
import threading

# Flask অ্যাপ
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# লগিং সক্রিয় করা
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# শুরু কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "স্বাগতম! আমি একটি ভিডিও ডাউনলোডার বট। শুধু ভিডিও লিঙ্ক পাঠান, আমি ডাউনলোড করে দিব।\n\n"
        "সমর্থিত: YouTube, Facebook, Instagram, Twitter, TikTok"
    )

# ভিডিও ডাউনলোড হ্যান্ডলার
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    api_url = f"https://api.vevioz.com/api/button/?url={url}"
    await update.message.reply_text("ভিডিও লিংক যাচাই করা হচ্ছে...")

    try:
        r = requests.get(api_url)
        if "Download" not in r.text:
            await update.message.reply_text("দুঃখিত! এই লিংক থেকে ভিডিও ডাউনলোড করা যাচ্ছে না।")
            return

        video_links = []
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            if "download" in a.text.lower():
                video_links.append((a.text.strip(), a['href']))

        if not video_links:
            await update.message.reply_text("ভিডিও ডাউনলোড লিঙ্ক খুঁজে পাওয়া যায়নি।")
            return

        msg = "নিচের ডাউনলোড লিঙ্কগুলো পাওয়া গেছে:\n\n"
        for name, link in video_links:
            msg += f"{name}:\n{link}\n\n"
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Download Error: {e}")
        await update.message.reply_text("একটি ত্রুটি ঘটেছে, পরে আবার চেষ্টা করুন।")

# মেইন ফাংশন
def main():
    threading.Thread(target=run_flask).start()  # Flask চালু করতে থ্রেড
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))

    application.run_polling()

if __name__ == '__main__':
    main()