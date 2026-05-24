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

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not found!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Send YouTube video link"
    )


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text(
        "📥 Downloading..."
    )

    try:

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        ydl_opts = {
            "format": "mp4",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        await msg.edit_text("📤 Uploading...")

        with open(file_path, "rb") as video:

            await update.message.reply_video(
                video=video,
                supports_streaming=True
            )

        os.remove(file_path)

        await msg.edit_text("✅ Done!")

    except Exception as e:

        await msg.edit_text(
            f"❌ Error:\n{str(e)}"
        )


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

    try:
        main()

    except Exception as e:
        print("CRASH ERROR:")
        print(e)
