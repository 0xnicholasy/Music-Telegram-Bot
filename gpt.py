import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from openai import OpenAI
from openai.types import Completion
import dotenv
import logging
import os
from database.message_history import MessageHistory
from logger import ClearLoggingObject, RespondLoggingObject

from utils import format_to_markdown_v2, get_current_day_str, split_string
from database.mongo import db
from telegram.helpers import escape_markdown

dotenv.load_dotenv()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename=f"logs/{get_current_day_str()}.log",
    filemode="w",
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("GPT"))


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        """
        Hello! I am your chatbot. You can start chatting with me.
    Just type your prompt in the chatroom and I will reply you.
    Use /clear to clear all archived conversations.
        """
    )


async def respond(update: Update, context: CallbackContext) -> None:
    try:
        message = update.message.text
        current_user = update.message.from_user
        chat_id = update.message.chat_id
        message_thread_id = update.message.message_thread_id

        # * get user object from db
        gpt_users = db["users"]
        user_query_filter = {"user_id": current_user.id}

        print(f"Message sent from chat: {update.message.chat}\nPrompt: {message}")
        print(f"Message thread_id: {message_thread_id}")
        processing_text = await update.message.reply_text("processing...", quote=True)

        # * query past messages from db by (chat id, message thread id)
        message_histories = db["message_histories"]
        query_filter = {"id": chat_id, "thread_id": message_thread_id}
        query_result = message_histories.find_one(query_filter)
        # print(f"==>> query_result: {query_result}")
        new_history = True
        message_history: MessageHistory = MessageHistory(
            chat_id,
            message_thread_id,
            "gpt-4-turbo-preview",
            [
                {
                    "role": "system",
                    "content": "You are chatting with a professional AI assistant.",
                },
            ],
        )
        # print(f"==>> message_history: MessageHistory: {message_history}")
        if query_result:
            new_history = False
            message_history = MessageHistory(**query_result)

        message_history.messages.append({"role": "user", "content": message})
        response: Completion = client.chat.completions.create(
            model="gpt-4-turbo-preview", messages=message_history.messages
        )

        # async for chunk in response:
        best_response = split_string(response.choices[0].message.content)
        print(f"Number of response choices: {len(response.choices)}")

        for msg in best_response:  # * send response in telegram
            # logger.info(msg)
            formatted_msg = format_to_markdown_v2(escape_markdown(msg, version=2))
            await update.message.reply_markdown_v2(formatted_msg, quote=True)

        # * add response to object's message
        message_history.messages.append(
            {"role": "system", "content": response.choices[0].message.content}
        )
        if new_history:
            # * save past messages to db
            history_dict = message_history.__dict__
            history_dict.pop("_id")
            message_histories.insert_one(history_dict)
            print("Added new history to db")
        else:
            # * update messages to db
            message_histories.update_one(
                query_filter, {"$set": {"messages": message_history.messages}}
            )
            print("Updated new history to db")
        respond_logging_obj = RespondLoggingObject(
            update.message.chat,
            message_thread_id,
            prompt=message,
            response=response.choices[0].message.content,
            new_conversation=new_history,
        )
        logger.info(respond_logging_obj)
        gpt_users.find_one_and_update(
            user_query_filter,
            {
                "$inc": {"asking_count.success": 1},
                "$setOnInsert": {
                    "username": current_user.username,
                    "user_id": current_user.id,
                    "asking_count.failed": 0,
                },
            },
            upsert=True,
        )
    except Exception as e:
        logger.error(e)
        await update.message.reply_text(
            "Unexpected error occurred, failed to send reply"
        )
        gpt_users.find_one_and_update(
            user_query_filter,
            {
                "$inc": {"asking_count.failed": 1},
                "$setOnInsert": {
                    "username": current_user.username,
                    "user_id": current_user.id,
                    "asking_count.success": 0,
                },
            },
            upsert=True,
        )
    finally:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=processing_text.id
        )


async def clear(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    message_thread_id = update.message.message_thread_id

    print(f"Clear request sent from chat: {update.message.chat}")
    print(f"Clear request thread_id: {message_thread_id}")

    # TODO: query past messages from db by (chat id, message thread id)
    message_histories = db["message_histories"]
    query_filter = {"id": chat_id, "thread_id": message_thread_id}
    message_histories.delete_one(query_filter)
    await update.message.reply_text("Past conversations cleared!")
    clear_logging_obj = ClearLoggingObject(update.message.chat, message_thread_id)
    logger.info(clear_logging_obj)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("GPT_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))
    application.add_handler(CommandHandler("clear", clear))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
