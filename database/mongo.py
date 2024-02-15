from pymongo import MongoClient
from pymongo.collection import Collection

from .message_history import MessageHistory

client = MongoClient("mongodb://localhost:27017")
db = client["message_histories"]


def test_insert():
    message_histories = db["message_histories"]
    sample_history: MessageHistory = {
        "id": -10,
        "thread_id": None,
        "model": "gpt-4-turbo-preview",
        "messages": [
            {"role": "system", "content": "You are chatting with an AI assistant."},
            {"role": "user", "content": "Good Morning"},
        ],
    }
    message_histories.insert_one(sample_history)
    sample_history = {
        "id": -10000,
        "thread_id": 6,
        "model": "gpt-4-turbo-preview",
        "messages": [
            {
                "role": "system",
                "content": "You are chatting with a professional AI assistant.",
            },
            {"role": "user", "content": "I want to learn Japanese"},
        ],
    }
    message_histories.insert_one(sample_history)


def test_query():
    message_histories = db["message_histories"]
    query_result = message_histories.find_one({"id": -10000})
    print(query_result)
    print(f"type of query result: {type(query_result)}")
    message_history = MessageHistory(**query_result)
    print(message_history)
    message_history = MessageHistory(**message_histories.find_one({"id": 0}))
    print(message_history)


if __name__ == "__main__":
    # test_insert()
    test_query()
