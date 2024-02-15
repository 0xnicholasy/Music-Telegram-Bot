from dataclasses import dataclass
from types import NoneType
from typing import Any, Iterable, List, Optional
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam


@dataclass
class MessageHistory:
    """Class for keeping track of an item in inventory."""

    id: int
    thread_id: int | NoneType
    model: str
    messages: List[ChatCompletionMessageParam]
    _id: Optional[Any] = None
