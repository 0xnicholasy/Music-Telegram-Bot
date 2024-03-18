from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Tuple, Optional

Roles = Literal["user", "admin", "blacklisted"]


@dataclass
class GPTUser:
    """Class for tracking users using this bot"""

    user_id: int
    username: str
    role: Roles = "user"
    asking_count: Dict[Literal["success", "failed"], int] = field(default_factory=dict)
    _id: Optional[Any] = None
    tokens_used: Dict[Literal["prompt", "completion"], int] = field(
        default_factory=dict
    )
