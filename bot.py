import os
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a YouTube video link and I will download it."
    )


# Download function
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    msg = await update.message.reply_text("📥 Downloading video...")

    try:
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": "video.%(ext)s",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        await msg.edit_text("📤 Uploading video...")

        with open(file_name, "rb") as video:
            await update.message.reply_video(video=video)

        os.remove(file_name)

        await msg.edit_text("✅ Done!")

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{str(e)}")


# Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, download_video)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
