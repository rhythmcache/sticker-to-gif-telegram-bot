import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import ffmpeg
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
# Telegram Bot Token
BOT_TOKEN = "Enter Your Bot Token Here"
##################################
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True
async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Send me a sticker, and I'll convert it to PNG or GIF for you!"
    )
async def handle_sticker(update: Update, context: CallbackContext) -> None:
    """Handle incoming stickers."""
    user = update.message.from_user
    sticker = update.message.sticker
    sticker_file = await sticker.get_file()
    sticker_path = os.path.join(TEMP_DIR, f"{sticker.file_id}.webp")
    await sticker_file.download_to_drive(sticker_path)
    is_animated = sticker.is_animated or sticker.is_video
    if is_animated:
        output_path = os.path.join(TEMP_DIR, f"{sticker.file_id}.gif")
        (
            ffmpeg.input(sticker_path)
            .output(output_path)
            .run(overwrite_output=True)
        )
        await update.message.reply_document(document=open(output_path, "rb"))
        os.remove(output_path)
    else:
        output_path = os.path.join(TEMP_DIR, f"{sticker.file_id}.png")
        (
            ffmpeg.input(sticker_path)
            .output(output_path)
            .run(overwrite_output=True)
        )
        await update.message.reply_document(document=open(output_path, "rb"))
        os.remove(output_path)
    os.remove(sticker_path)
async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors."""
    logger.error(f"Update {update} caused error: {context.error}")
def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    application.add_error_handler(error_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
  
