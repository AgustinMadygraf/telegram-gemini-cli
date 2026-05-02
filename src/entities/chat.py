"""
Path: src/entities/chat.py
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatMessage:
    chat_id: int
    user_id: int
    text: str
    username: Optional[str] = None
