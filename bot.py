import logging
import os

from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from filter import YoutubePlaylistFilter

from music import play
import dotenv
    
dotenv.load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='1'),
         InlineKeyboardButton("Option 2", callback_data='2')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Please choose:', reply_markup=reply_markup)


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
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TOKEN")).build()

    application.add_handler(CommandHandler('start', help_command))
    # application.add_handler(CallbackQueryHandler(button))

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(YoutubePlaylistFilter(), play))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES,)


if __name__ == "__main__":
    main()