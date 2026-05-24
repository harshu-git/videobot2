import os
import uuid
import random
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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Send YouTube video link."
    )


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text(
        "📥 Downloading..."
    )

    try:

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        unique_id = str(uuid.uuid4())

        output_template = f"downloads/{unique_id}.%(ext)s"

        ydl_opts = {
            "format": "bv*+ba/b",
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "cookiefile": "cookies.txt",
            "quiet": True,
            "noplaylist": True,

            "http_headers": {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9",
            },

            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            downloaded_file = None

            for file in os.listdir("downloads"):

                if file.startswith(unique_id):

                    downloaded_file = os.path.join(
                        "downloads",
                        file
                    )

                    break

            if not downloaded_file:
                raise Exception("Download failed.")

        await msg.edit_text("📤 Uploading...")

        with open(downloaded_file, "rb") as video:

            await update.message.reply_video(
                video=video,
                supports_streaming=True
            )

        # Cleanup
        os.remove(downloaded_file)

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

    print("Bot running on Render...")

    app.run_polling()


if __name__ == "__main__":
    main()
