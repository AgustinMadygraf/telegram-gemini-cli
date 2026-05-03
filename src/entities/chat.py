"""
Path: src/entities/chat.py
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

@dataclass
class ChatMessage:
    chat_id: int
    user_id: int
    text: str
    role: str = "user" # "user" o "assistant"
    username: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    photo_ids: Optional[List[str]] = None

    @property
    def is_command(self) -> bool:
        return self.text.startswith("/") and self.role == "user"
