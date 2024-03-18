from openai import OpenAI
from openai.types import Completion
import os, dotenv

dotenv.load_dotenv()

model = "gpt-4-turbo-preview"
messages = (
    [
        {
            "role": "system",
            "content": "You are chatting with a professional AI assistant.",
        },
        {"role": "user", "content": "Hello"},
    ],
)

if __name__ == "__main__":
    openai_keys = [os.getenv("GPT-FIRST"), os.getenv("GPT-SECOND")]
    print(openai_keys)
    client = OpenAI(api_key=openai_keys[1])
    response = client.chat.completions.create(model=model, messages=messages)
    print(response)
