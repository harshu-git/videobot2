import os
import yt_dlp

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Send me a YouTube link and I will download it."
    )


# DOWNLOAD FUNCTION
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    status_message = await update.message.reply_text(
        "📥 Downloading video..."
    )

    try:
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "cookiefile": "cookies.txt",
            "quiet": True,
            "noplaylist": True,
        }

        # Create downloads folder
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await status_message.edit_text("📤 Uploading video...")

        # Telegram upload
        with open(file_path, "rb") as video:
            await update.message.reply_video(
                video=video,
                supports_streaming=True
            )

        # Delete downloaded file after upload
        os.remove(file_path)

        await status_message.edit_text("✅ Done!")

    except Exception as e:
        await status_message.edit_text(
            f"❌ Error:\n{str(e)}"
        )


# MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            download_video
        )
    )

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
