from abc import ABC

from telegram import Chat


class BaseLoggingObject(ABC):
    type: str
    chat: Chat
    thread_id: int

    def __init__(self, type: str, chat: Chat, thread_id: int) -> None:
        super().__init__()
        self.type = type
        self.chat = chat
        self.thread_id = thread_id

    def __repr__(self) -> str:
        return f"type: {self.type}, chat: {self.chat}, thread_id: {self.thread_id}, "


class RespondLoggingObject(BaseLoggingObject):
    new_conversation: bool
    prompt: str
    response: str

    def __init__(
        self,
        chat: Chat,
        thread_id: int,
        prompt: str,
        response: str,
        new_conversation=False,
    ) -> None:
        super().__init__("prompt", chat, thread_id)
        self.prompt = prompt
        self.response = response
        self.new_conversation = new_conversation

    def __repr__(self) -> str:
        return (
            super().__repr__()
            + f"prompt: {self.prompt}, response: {self.response[:100]}..., new_conversation: {self.new_conversation}"
        )


class ClearLoggingObject(BaseLoggingObject):
    def __init__(self, chat: Chat, thread_id: int) -> None:
        super().__init__("/clear", chat, thread_id)

    def __repr__(self) -> str:
        return super().__repr__()
