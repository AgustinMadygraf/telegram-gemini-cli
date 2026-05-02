"""
Path: src/infrastructure/setting/config.py
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from typing import List, Optional
import os

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    ALLOWED_CHAT_IDS: List[int]
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""
    CLOUDFLARE_TOKEN: str = ""
    GEMINI_BINARY_PATH: str = "/usr/local/bin/gemini"
    GEMINI_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
