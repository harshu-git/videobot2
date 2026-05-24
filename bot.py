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

# ─────────────────────────────────────────────

# BOT TOKEN

# ─────────────────────────────────────────────

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ─────────────────────────────────────────────

# START MESSAGE

# ─────────────────────────────────────────────

WELCOME_MESSAGE = (
"👋 Welcome to Harsh's Downloader Bot 🚀\n\n"
"📥 Send any YouTube link\n"
"🎬 I'll download the video instantly\n\n"
"⚡ Fast • Simple • HD Quality\n\n"
"👨‍💻 Created by Harsh Shrimalii\n"
"📷 https://instagram.com/framesbyharshhh"
)

# ─────────────────────────────────────────────

# START COMMAND

# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
await update.message.reply_text(
    WELCOME_MESSAGE
)
```

# ─────────────────────────────────────────────

# DOWNLOAD FUNCTION

# ─────────────────────────────────────────────

def download_video(url):

```
os.makedirs("downloads", exist_ok=True)

output_template = "downloads/%(title)s.%(ext)s"

ydl_opts = {
    "format": "best[ext=mp4]",
    "outtmpl": output_template,
    "quiet": True,
    "noplaylist": True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:

    info = ydl.extract_info(url, download=True)

    return ydl.prepare_filename(info)
```

# ─────────────────────────────────────────────

# HANDLE USER MESSAGE

# ─────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
url = update.message.text.strip()

if "youtube.com" not in url and "youtu.be" not in url:

    await update.message.reply_text(
        "❌ Please send a valid YouTube link"
    )

    return

msg = await update.message.reply_text(
    "⏳ Downloading video..."
)

try:

    file_path = download_video(url)

    if not os.path.exists(file_path):

        await msg.edit_text(
            "❌ Download failed"
        )

        return

    size_mb = os.path.getsize(file_path) / (1024 * 1024)

    if size_mb > 49:

        await msg.edit_text(
            "⚠️ File too large for Telegram"
        )

        os.remove(file_path)

        return

    await msg.edit_text(
        "📤 Uploading video..."
    )

    with open(file_path, "rb") as video_file:

        await update.message.reply_video(
            video=video_file,
            caption="✅ Download Complete!",
            supports_streaming=True,
        )

    os.remove(file_path)

    await msg.delete()

except Exception as e:

    await msg.edit_text(
        f"❌ Error:\n{str(e)}"
    )
```

# ─────────────────────────────────────────────

# MAIN FUNCTION

# ─────────────────────────────────────────────

def main():

```
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("🤖 Bot is running...")

app.run_polling()
```

# ─────────────────────────────────────────────

# RUN BOT

# ─────────────────────────────────────────────

if **name** == "**main**":
main()
