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

# Fetch standard token variable securely from Railway environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    logger.critical("❌ DEPLOYMENT FAILED: Missing 'TELEGRAM_BOT_TOKEN' in Railway variables!")
    sys.exit(1)

BOT_TOKEN = BOT_TOKEN.strip().replace('"', '').replace("'", "")

# Configured to mimic official mobile app requests (bypasses datacenter blocks)
YTDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': '%(id)s.%(ext)s',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios'], # Rotates mobile signatures to bypass cloud hosting restrictions
        }
    }
}

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

        # Catch instances where files are auto-renamed during container processing
        if filename and not os.path.exists(filename):
            base, _ = os.path.splitext(filename)
            if os.path.exists(f"{base}.mp4"):
                filename = f"{base}.mp4"

        if filename and os.path.exists(filename):
            with open(filename, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption="Here is your video! 🎬"
                )
            await msg.delete()
            logger.info("Video sent successfully.")
        else:
            raise FileNotFoundError("System failed to generate file output payload.")

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
