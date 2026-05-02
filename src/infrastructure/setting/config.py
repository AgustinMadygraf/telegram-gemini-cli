"""
Path: src/infrastructure/setting/config.py
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    ALLOWED_CHAT_IDS: List[int]
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""
    CLOUDFLARE_TOKEN: str = ""
    
    # Configuración Gemini
    GEMINI_BINARY_PATH: str = "/usr/local/bin/gemini"
    GEMINI_AUTH_METHOD: str = "api_key"
    GEMINI_API_KEY: Optional[str] = None
    
    # Configuración Vertex AI
    VERTEX_PROJECT_ID: Optional[str] = None
    VERTEX_LOCATION: str = "us-central1"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
