import os
import yt_dlp
from telegram import Update
from telegram.ext import (
ApplicationBuilder,
MessageHandler,
ContextTypes,
filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
"👋 Welcome to Harsh's Downloader Bot! 🚀\n\n"
"📥 Send any YouTube video link\n"
"🎬 I'll download and send it back\n\n"
"⚡ Fast • High Quality • Easy to Use\n\n"
"👨‍💻 Created by Harsh Shrimalii\n"
"📷 https://instagram.com/framesbyharshhh"
)

# ─────────────────────────────────────────────

def download_video(url, output_path):

```
ydl_opts = {
    "format": "best[ext=mp4]",
    "outtmpl": output_path,
    "quiet": True,
    "noplaylist": True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
```

# ─────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
url = update.message.text.strip()

if "youtube.com" not in url and "youtu.be" not in url:
    await update.message.reply_text(
        "❌ Send a valid YouTube link"
    )
    return

msg = await update.message.reply_text(
    "⏳ Downloading video..."
)

os.makedirs("downloads", exist_ok=True)

output_path = "downloads/video.%(ext)s"

try:

    download_video(url, output_path)

    file_path = None

    for file in os.listdir("downloads"):
        file_path = os.path.join("downloads", file)

    if not file_path:
        await msg.edit_text("❌ Download failed")
        return

    size_mb = os.path.getsize(file_path) / (1024 * 1024)

    if size_mb > 49:
        await msg.edit_text(
            "⚠️ File too large for Telegram"
        )
        os.remove(file_path)
        return

    await msg.edit_text("📤 Uploading...")

    with open(file_path, "rb") as f:

        await update.message.reply_video(
            video=f,
            caption="✅ Download complete!",
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

def main():

```
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(filters.COMMAND, start)
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

print("🤖 Bot running...")

app.run_polling()
```

# ─────────────────────────────────────────────

if **name** == "**main**":
main()
