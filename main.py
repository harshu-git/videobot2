import os
import sys
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch variables securely from Railway environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RAW_COOKIES = os.getenv("YOUTUBE_COOKIES_DATA")

if not BOT_TOKEN:
    logger.critical("❌ DEPLOYMENT FAILED: Missing 'TELEGRAM_BOT_TOKEN' in Railway variables!")
    sys.exit(1)

BOT_TOKEN = BOT_TOKEN.strip().replace('"', '').replace("'", "")
COOKIE_FILE_PATH = "temp_youtube_cookies.txt"

# General configuration options
YTDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True
}

# Securely rebuild cookie file from environment variable during runtime initialization
if RAW_COOKIES:
    try:
        with open(COOKIE_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(RAW_COOKIES.strip())
        logger.info("🔒 Secure Verification: Generated dynamic cookie file from environment data.")
        YTDL_OPTIONS['cookiefile'] = COOKIE_FILE_PATH
    except Exception as creation_error:
        logger.error(f"❌ Failed to parse secure cookie variable: {str(creation_error)}")
else:
    logger.warning("⚠️ Warning: No 'YOUTUBE_COOKIES_DATA' variable detected. Expecting 403 challenges on YouTube links.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me any social media video link, and I will download it!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid web link.")
        return

    logger.info(f"Processing URL: {url}")
    msg = await update.message.reply_text("📥 Processing video... Please wait.")

    filename = None
    try:
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename) and os.path.exists(f"{filename}.mp4"):
            filename = f"{filename}.mp4"

        if os.path.exists(filename):
            with open(filename, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption="Here is your video! 🎬"
                )
            await msg.delete()
            logger.info("Video sent successfully.")
        else:
            raise FileNotFoundError("Downloaded file missing from workspace volume.")

    except Exception as e:
        logger.error(f"Download processing failed: {str(e)}")
        await msg.edit_text(f"❌ Download failed.\n`{str(e)}`", parse_mode='Markdown')
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    logger.info("🤖 Starting Telegram Downloader Bot Application...")
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        logger.info("✅ System Active. Polling Telegram network pipelines...")
        application.run_polling()
    except Exception as initialization_error:
        logger.critical(f"❌ Core engine crash during authorization setup: {str(initialization_error)}")
        sys.exit(1)
