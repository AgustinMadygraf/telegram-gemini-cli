from dataclasses import dataclass
from typing import Optional

@dataclass
class AIResponse:
    text: str
    success: bool
    error_message: Optional[str] = None
