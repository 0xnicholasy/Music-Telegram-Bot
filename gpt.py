import datetime
from typing import List
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from openai import OpenAI, RateLimitError
from openai.types import Completion
import dotenv
import logging
import os
from database.message_history import MessageHistory
from database.user import GPTUser
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
openai_keys = [os.getenv("GPT-FIRST"), os.getenv("GPT-SECOND")]
print(f"openai_keys: {openai_keys}")
gpt_key = openai_keys[1]
client = OpenAI(api_key=gpt_key)
print(f"using first priority api key: {gpt_key}")

# Replace 'YOUR_TOKEN' with your bot's access token
bot_token = "YOUR_TOKEN"
bot = Bot(token=os.getenv("GPT_BOT_TOKEN"))

gpt_model = "gpt-3.5-turbo"
# gpt_model = "gpt-4-turbo-preview"


def get_admins():
    gpt_users = db["users"]
    user_query_filter = {"role": "admin"}
    admin_cursor = gpt_users.find(user_query_filter)

    # Process the cursor and fetch results
    admins: List[GPTUser] = []
    for admin in admin_cursor:
        admins.append(GPTUser(**admin))

    return admins


def is_admin(user_id: int):
    # * get user object from db
    gpt_users = db["users"]
    user_query_filter = {"user_id": user_id}
    user_collection = gpt_users.find_one(user_query_filter)
    if user_collection:
        user = GPTUser(**user_collection)
        return user.role == "admin"
    return False


async def notify_admin(admin_user_id: int, message: str):
    await bot.send_message(chat_id=admin_user_id, text=message)


def get_admins():
    gpt_users = db["users"]
    user_query_filter = {"role": "admin"}
    admin_cursor = gpt_users.find(user_query_filter)

    # Process the cursor and fetch results
    admins: List[GPTUser] = []
    for admin in admin_cursor:
        admins.append(GPTUser(**admin))

    return admins


def is_admin(user_id: int):
    # * get user object from db
    gpt_users = db["users"]
    user_query_filter = {"user_id": user_id}
    user_collection = gpt_users.find_one(user_query_filter)
    if user_collection:
        user = GPTUser(**user_collection)
        return user.role == "admin"
    return False


async def notify_admin(admin_user_id: int, message: str):
    await bot.send_message(chat_id=admin_user_id, text=message)


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        """
        Hello! I am your chatbot. You can start chatting with me.
    Just type your prompt in the chatroom and I will reply you.
    Use /clear to clear all archived conversations.
        """
    )


async def chat(update: Update, context: CallbackContext) -> None:
    try:
        message = update.message.text
        current_user = update.message.from_user
        chat_id = update.message.chat_id
        message_thread_id = update.message.message_thread_id
        admins = get_admins()

        # * get user object from db
        gpt_users = db["users"]
        user_query_filter = {"user_id": current_user.id}
        user_collection = gpt_users.find_one(user_query_filter)
        print(datetime.datetime.now().ctime())
        if user_collection:
            user = GPTUser(**user_collection)
            if user.role == "blacklisted":
                print(f"user: {user} is blacklisted")
                # await update.message.reply_text(
                #     "You have been backlisted from the bot", quote=True
                # )
                return

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
            gpt_model,
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
            model=gpt_model, messages=message_history.messages
        )

        # async for chunk in response:
        best_response = split_string(response.choices[0].message.content)
        tokens_used = {
            "prompt": response.usage.prompt_tokens,
            "completion": response.usage.completion_tokens,
        }
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

            for admin in admins:
                await notify_admin(
                    admin.user_id,
                    f"New user with following details\n{current_user.to_json()}",
                )
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
                "$inc": {
                    "asking_count.success": 1,
                    "tokens_used.prompt": tokens_used["prompt"],
                    "tokens_used.completion": tokens_used["completion"],
                },
                "$setOnInsert": {
                    "username": current_user.username,
                    "user_id": current_user.id,
                    "asking_count.failed": 0,
                    "role": "user",
                },
            },
            upsert=True,
        )
    except (
        RateLimitError
    ) as rle:  # switch to second api endpoint if the first one exceed limit
        globals()["client"] = OpenAI(api_key=openai_keys[1])
        logger.debug(f"using first priority api key: {openai_keys[1]}")
        await chat(update, context)
    except Exception as e:
        logger.error(e)
        print(type(e))
        await update.message.reply_text(
            f"Following unexpected error occurred, failed to send reply:\n{e}\nPlease try again"
        )
        gpt_users.find_one_and_update(
            user_query_filter,
            {
                "$inc": {
                    "asking_count.success": 1,
                    "tokens_used.prompt": tokens_used["prompt"],
                    "tokens_used.completion": tokens_used["completion"],
                },
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


async def blacklist(update: Update, context: CallbackContext):
    args = update.message.text.split(" ")

    if len(args) == 1:
        await update.message.reply_text("User id must not be emptied")
        return
    user_id = int(args[1])

    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("You are not authorized to call this command!")
        return
    print(f"blacklisting user id: {user_id}")
    gpt_users = db["users"]
    receipt = gpt_users.update_one(
        {"user_id": user_id}, {"$set": {"role": "blacklisted"}}
    )
    if receipt.modified_count:
        await update.message.reply_text(f"Blacklisted user {user_id}!")
    else:
        await update.message.reply_text(f"User {user_id} not found from db!")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("GPT_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(CommandHandler("blacklist", blacklist))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
