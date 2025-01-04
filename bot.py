# Sticker2gif by github.com/rhythmcache
# rhythmcache.t.me

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import ffmpeg

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Token
BOT_TOKEN = "Enter Your Bot Token Here"

# Temporary directory to store files
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)  # Fixed missing parenthesis

async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Send me a sticker, and I'll convert it to PNG or GIF for you!"
    )

async def handle_sticker(update: Update, context: CallbackContext) -> None:
    """Handle incoming stickers."""
    user = update.message.from_user
    sticker = update.message.sticker

    # Download the sticker file
    sticker_file = await sticker.get_file()
    sticker_path = os.path.join(TEMP_DIR, f"{sticker.file_id}.webp")
    await sticker_file.download_to_drive(sticker_path)

    # Check if the sticker is animated or static
    is_animated = sticker.is_animated or sticker.is_video

    if is_animated:
        # Convert animated sticker to GIF
        output_path = os.path.join(TEMP_DIR, f"{sticker.file_id}.gif")
        (
            ffmpeg.input(sticker_path)
            .output(output_path)
            .run(overwrite_output=True)
        )
        await update.message.reply_document(document=open(output_path, "rb"))
        os.remove(output_path)
    else:
        # Convert static sticker to PNG
        output_path = os.path.join(TEMP_DIR, f"{sticker.file_id}.png")
        (
            ffmpeg.input(sticker_path)
            .output(output_path)
            .run(overwrite_output=True)
        )
        await update.message.reply_document(document=open(output_path, "rb"))
        os.remove(output_path)

    # Clean up the original sticker file
    os.remove(sticker_path)

async def handle_non_sticker(update: Update, context: CallbackContext) -> None:
    """Handle non-sticker messages."""
    await update.message.reply_text(
        "Please send me a sticker, and I'll convert it to PNG or GIF for you!"
    )

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors."""
    logger.error(f"Update {update} caused error: {context.error}")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    application.add_handler(MessageHandler(~filters.Sticker.ALL, handle_non_sticker))  # Handle non-sticker messages
    application.add_error_handler(error_handler)

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
