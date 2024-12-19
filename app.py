import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from moviepy.config import IMAGEMAGICK_BINARY
from helper import linkdownload, add_watermark, merge_outro, upload_to_youtube, cleanup_downloads

# Set ImageMagick binary path (This should point to the location where ImageMagick is installed)
IMAGEMAGICK_BINARY = "/usr/bin/convert"  # Default location of ImageMagick in many Linux systems

# Telegram bot configuration
API_ID = "your_api_id"  # Replace with your API ID
API_HASH = "your_api_hash"  # Replace with your API hash
BOT_TOKEN = "your_bot_token"  # Replace with your bot token
app = Client("instagram_to_youtube_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------- Telegram Bot Handlers --------

@app.on_message(filters.command("start"))
def start_handler(client, message: Message):
    """Handles /start command"""
    message.reply("Welcome to Instagram to YouTube Bot! Send me an Instagram post/reel link to get started.")

@app.on_message(filters.text & ~filters.command)
def process_link(client, message: Message):
    """Handles the received Instagram link, processes it, and uploads to YouTube"""
    link = message.text.strip()

    # Step 1: Download the video
    message.reply("Downloading video from Instagram...")
    video_path, video_title = linkdownload(link)
    if not video_path.endswith(".mp4"):
        message.reply(f"Download error: {video_title}")
        cleanup_downloads()
        return

    # Step 2: Add watermark to the video
    message.reply("Adding watermark to the video...")
    time.sleep(2)
    watermarked_path = add_watermark(video_path)
    if not watermarked_path:
        message.reply("Failed to add watermark.")
        cleanup_downloads()
        return

    # Step 3: Merge outro with the video
    message.reply("Merging outro with fade effect...")
    outro_path = r"C:\\Users\\mujeem khan\\Desktop\\Youtube Uploader\\output.mp4"  # Replace with your outro file path
    video_with_outro_path = f"final_{os.path.basename(watermarked_path)}"
    final_video_path = merge_outro(watermarked_path, outro_path, video_with_outro_path)
    if not final_video_path:
        message.reply("Failed to merge outro.")
        cleanup_downloads()
        return

    # Step 4: Upload to YouTube
    message.reply("Uploading video to YouTube...")
    try:
        upload_to_youtube(
            file_path=final_video_path,
            title=video_title,
            description="Welcome to Be Positive!\n\nThis channel is dedicated to helping you find motivation, positivity, and inspiration to live your best life...",
            tags=["shorts", "be positive", "motivation", "high", "instagram", "bpositive", "ytshorts", "reels", "reel"],
            category_id="22",
            privacy_status="public"
        )
        message.reply("Video uploaded successfully to YouTube!")
    except Exception as e:
        message.reply(f"An error occurred during upload: {e}")
    finally:
        cleanup_downloads()

# Run the bot
if __name__ == "__main__":
    app.run()
