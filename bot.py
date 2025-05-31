import logging
import os
import shutil

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackContext,
)
from filter import YoutubePlaylistFilter

from music.music import play
import dotenv

dotenv.load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def cleanup_downloads() -> None:
    """Clean up downloads directory on bot startup."""
    downloads_dir = "downloads"
    
    try:
        if os.path.exists(downloads_dir):
            # Get all items in downloads directory
            for item in os.listdir(downloads_dir):
                item_path = os.path.join(downloads_dir, item)
                
                # Keep .gitkeep files and NA directory
                if item.startswith("."):
                    continue
                elif item == "NA":
                    # Clean out files inside NA directory but keep the directory
                    if os.path.isdir(item_path):
                        for na_item in os.listdir(item_path):
                            na_item_path = os.path.join(item_path, na_item)
                            if na_item != ".gitkeep":  # Keep .gitkeep in NA directory too
                                if os.path.isfile(na_item_path):
                                    os.remove(na_item_path)
                                    logger.info(f"Removed file: {na_item_path}")
                                elif os.path.isdir(na_item_path):
                                    shutil.rmtree(na_item_path)
                                    logger.info(f"Removed directory: {na_item_path}")
                else:
                    # Remove all other files and directories
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        logger.info(f"Removed file: {item_path}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        logger.info(f"Removed directory: {item_path}")
        
        # Ensure NA directory exists
        na_dir = os.path.join(downloads_dir, "NA")
        os.makedirs(na_dir, exist_ok=True)
        logger.info("Downloads directory cleanup completed")
        
    except Exception as e:
        logger.error(f"Error during downloads cleanup: {e}")


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send me the youtube playlist link to play music.")


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Echo the user message."""
#     await update.message.reply_text(update.message.text)


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


def main() -> None:
    """Start the bot."""
    # Clean up downloads directory on startup
    cleanup_downloads()
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TOKEN")).build()

    application.add_handler(CommandHandler("start", help_command))
    # application.add_handler(CallbackQueryHandler(button))

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(YoutubePlaylistFilter(), play))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
