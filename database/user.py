from dataclasses import dataclass
from typing import Dict, Literal, Tuple

from telegram import User


@dataclass
class GPTUser:
    """Class for tracking users using this bot"""

    user_id: int
    username: str
    asking_count: Dict[Literal["success", "failed"], int] = {"success": 0, "failed": 0}
    tokens_used: Dict[Literal["prompt", "completion"], int] = {
        "prompt": 0,
        "completion": 0,
    }
