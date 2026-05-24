import os
import sys
import logging
import requests
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("❌ DEPLOYMENT FAILED: Missing 'TELEGRAM_BOT_TOKEN' in Railway variables!")
    sys.exit(1)

BOT_TOKEN = BOT_TOKEN.strip().replace('"', '').replace("'", "")

# Extract cleaner YouTube Video ID from any regular or Shorts URL
def extract_video_id(url):
    pattern = r'(?:v=|\/shorts\/|\/embed\/|\/v\/|youtu\.be\/|\/v=|^)([^#\&\?^\/]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me any social media video link, and I will download it!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid web link.")
        return

    logger.info(f"Processing URL: {url}")
    msg = await update.message.reply_text("📥 Fetching stream links... Please wait.")

    # -------------------------------------------------------------
    # ROUTE A: HIGH-SPEED BYPASS FOR YOUTUBE & YOUTUBE SHORTS
    # -------------------------------------------------------------
    if "youtube.com" in url or "youtu.be" in url:
        video_id = extract_video_id(url)
        if not video_id:
            await msg.edit_text("❌ Could not extract a valid YouTube Video ID.")
            return

        try:
            # Connect to a rapid open-source third-party media infrastructure pipeline
            api_url = f"https://cobalt.tools"
            payload = {
                "url": f"https://youtube.com{video_id}",
                "videoQuality": "720",
                "downloadMode": "video"
            }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                download_url = result.get("url")
                
                if download_url:
                    await msg.edit_text("🚀 Downloading media file stream payload...")
                    
                    # Stream the remote data chunk instantly straight into memory
                    video_data = requests.get(download_url, stream=True, timeout=30)
                    
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=video_data.content,
                        filename=f"{video_id}.mp4",
                        caption="Here is your video! 🎬"
                    )
                    await msg.delete()
                    logger.info("YouTube video delivered successfully via offloaded API pipeline.")
                    return
            
            raise Exception("API gateway did not return a valid download URL path.")

        except Exception as api_err:
            logger.error(f"Route A Bypass failed: {str(api_err)}. Swapping to standard extraction profile...")
            # If the remote API gateway encounters traffic limits, the code automatically falls back to Route B below

    # -------------------------------------------------------------
    # ROUTE B: UNIVERSAL EXTRACTOR FOR INSTAGRAM, TIKTOK, TWITTER
    # -------------------------------------------------------------
    import yt_dlp
    filename = None
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['mweb', 'tv_embedded']}}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if filename and not os.path.exists(filename):
            base, _ = os.path.splitext(filename)
            for ext in ['mp4', 'mkv', 'webm']:
                if os.path.exists(f"{base}.{ext}"):
                    filename = f"{base}.{ext}"
                    break

        if filename and os.path.exists(filename):
            with open(filename, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption="Here is your video! 🎬"
                )
            await msg.delete()
        else:
            raise FileNotFoundError("Target format file missing from workspace volume.")

    except Exception as e:
        logger.error(f"Download processing failed completely: {str(e)}")
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
        application.run_polling()
    except Exception as initialization_error:
        logger.critical(f"❌ Core engine crash during authorization setup: {str(initialization_error)}")
        sys.exit(1)
