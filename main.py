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

# Rebuild cookie file safely from environment variable if present
if RAW_COOKIES:
    try:
        with open(COOKIE_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(RAW_COOKIES.strip())
        logger.info("🔒 Secure Verification: Generated dynamic cookie file from environment data.")
    except Exception as creation_error:
        logger.error(f"❌ Failed to parse secure cookie variable: {str(creation_error)}")

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
    
    # Core fallback chains to bypass 403 errors and format errors
    formats_to_try = [
        'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Plan A: MP4 Stitch
        'best',                                                    # Plan B: Direct Video Source
        'worst'                                                    # Plan C: Low-res bypass fallback
    ]

    for current_format in formats_to_try:
        try:
            ydl_opts = {
                'format': current_format,
                'outtmpl': '%(id)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                # Force network variables to avoid server-side bot flags
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
            }

            if os.path.exists(COOKIE_FILE_PATH):
                ydl_opts['cookiefile'] = COOKIE_FILE_PATH

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            # Exit loop early if download succeeds
            if filename and os.path.exists(filename):
                break
        except Exception as format_error:
            logger.warning(f"Format scheme {current_format} failed. Trying next sequence...")
            continue

    try:
        # Check standard matching extensions
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
            raise FileNotFoundError("YouTube video format completely restricted on this cloud host server IP region.")

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
