from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from openai import OpenAI
from openai.types import Completion
import dotenv
import logging
import os
import re

from utils import split_string

def escape_markdown(text):
    return re.sub(r'(_*[\~`>#\+=|{}.!-])', r'\\\1', text)

dotenv.load_dotenv()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("GPT"))

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am your chatbot. You can start chatting with me.')

async def respond(update: Update, context: CallbackContext) -> None:
    try:
        message = update.message.text
        print(f"Message sent from: {update._effective_user}\nPrompt: {message}")
        response: Completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are chatting with an AI assistant."},
                {"role": "user", "content": message},
            ],
            # stream=True
        )
        # async for chunk in response:
        best_response = split_string(response.choices[0].message.content)
        print(best_response or "")
        for msg in best_response:
            await update.message.reply_html(f"""{msg}""", quote=True)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text(e)


def main() -> None:

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("GPT_BOT_TOKEN")).build()

    application.add_handler(CommandHandler('start', start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~ filters.COMMAND, respond))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES,)

if __name__ == '__main__':
    main()
