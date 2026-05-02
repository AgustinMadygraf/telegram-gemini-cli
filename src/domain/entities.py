from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatMessage:
    chat_id: int
    user_id: int
    text: str
    username: Optional[str] = None

@dataclass
class AIResponse:
    text: str
    success: bool
    error_message: Optional[str] = None
