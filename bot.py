import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# yt-dlp options for downloading
YTDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me any Social Media or YouTube Shorts link, and I will download the video for you.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid URL.")
        return

    msg = await update.message.reply_text("📥 Processing your link, please wait...")

    try:
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Send the video to the user
        with open(filename, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video_file,
                caption="Here is your video! 🎬"
            )
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Failed to download the video. Error: \n`{str(e)}`", parse_mode='Markdown')
    finally:
        # Clean up the downloaded file from the server
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    # Initialize the Application and pass your BotFather Token
    application = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN_HERE").build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Start the Bot
    application.run_polling()
