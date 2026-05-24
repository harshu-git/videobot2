import os
import sys
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Detailed logging to pinpoint errors easily on Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch token safely from Railway environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    logger.critical("❌ DEPLOYMENT FAILED: The environment variable 'TELEGRAM_BOT_TOKEN' is missing in Railway!")
    sys.exit(1)

# Strip any accidental hidden spaces or quotes from the token string
BOT_TOKEN = BOT_TOKEN.strip().replace('"', '').replace("'", "")

if ":" not in BOT_TOKEN:
    logger.critical("❌ DEPLOYMENT FAILED: The value provided for 'TELEGRAM_BOT_TOKEN' does not look like a real Telegram token.")
    sys.exit(1)

# Optimizations for video parsing
YTDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot.")
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

        # Fallback handle if standard extension wrapper differs
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
            raise FileNotFoundError("Downloaded video file could not be located on the server disk.")

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
        
        logger.info("✅ Connection established! Bot is now polling for messages.")
        application.run_polling()
    except Exception as initialization_error:
        logger.critical(f"❌ Core engine crash during authorization setup: {str(initialization_error)}")
        sys.exit(1)
