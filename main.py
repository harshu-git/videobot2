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

# Secure Token Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("❌ DEPLOYMENT FAILED: Missing 'TELEGRAM_BOT_TOKEN' in Railway variables!")
    sys.exit(1)

BOT_TOKEN = BOT_TOKEN.strip().replace('"', '').replace("'", "")

def extract_video_id(url):
    """Cleanly extracts the 11-character video ID string from any YouTube layout variation."""
    pattern = r'(?:v=|\/shorts\/|\/embed\/|\/v\/|youtu\.be\/|\/v=|^)([^#\&\?^\/]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 **Welcome to the YouTube & Shorts Downloader!**\n\nSend me any YouTube video link or YouTube Shorts link, and I will deliver the file directly.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("❌ This bot is optimized exclusively for YouTube & YouTube Shorts links.")
        return

    video_id = extract_video_id(url)
    if not video_id:
        await update.message.reply_text("❌ Invalid link format. Could not process the YouTube Video ID.")
        return

    logger.info(f"Processing Video Target ID: {video_id}")
    msg = await update.message.reply_text("📥 Extracting stream pipelines... Please wait.")

    try:
        # Utilize a highly stable public endpoint cluster that processes bypass layouts automatically
        api_url = "https://cobalt.tools"
        payload = {
            "url": f"https://youtube.com{video_id}",
            "videoQuality": "720", # Optimized for clear playback within standard Telegram upload dimensions
            "downloadMode": "video"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Triggering API payload query
        response = requests.post(api_url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            download_url = result.get("url")
            
            if download_url:
                await msg.edit_text("🚀 Streaming video file data directly to chat...")
                
                # Pull the raw media data binary buffer straight into the platform server instance memory
                video_stream = requests.get(download_url, stream=True, timeout=30)
                
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_stream.content,
                    filename=f"{video_id}.mp4",
                    caption="Here is your requested video! 🎬"
                )
                await msg.delete()
                logger.info("Video delivered successfully.")
                return
        
        raise Exception("The parsing infrastructure is heavily overloaded right now. Please try again in a few moments.")

    except Exception as err:
        logger.error(f"Media extraction runtime crash: {str(err)}")
        await msg.edit_text(f"❌ Processing Error:\n`{str(err)}`", parse_mode='Markdown')

if __name__ == '__main__':
    logger.info("🤖 Starting Dedicated YouTube Endpoint Downloader Bot Application...")
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        application.run_polling()
    except Exception as initialization_error:
        logger.critical(f"❌ Core engine setup crash: {str(initialization_error)}")
        sys.exit(1)
