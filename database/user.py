from dataclasses import dataclass
from typing import Dict, Literal

from telegram import User


@dataclass
class GPTUser:
    """Class for tracking users using this bot"""

    user_id: int
    username: str
    asking_count: Dict[Literal["success", "failed"], int] = {"success": 0, "failed": 0}
