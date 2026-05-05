"""
Path: src/infrastructure/setting/config.py
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os
import secrets
from dotenv import set_key, load_dotenv

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    ALLOWED_CHAT_IDS: List[int]
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET_TOKEN: str = ""
    CLOUDFLARE_TOKEN: str = ""
    
    # Proveedor de IA (gemini_cli, ollama)
    AI_PROVIDER: str = "gemini_cli"
    
    # Configuración Gemini
    GEMINI_BINARY_PATH: str = "/usr/local/bin/gemini"
    GEMINI_AUTH_METHOD: str = "api_key"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_WORKSPACE: Optional[str] = None
    
    # Configuración Vertex AI
    VERTEX_PROJECT_ID: Optional[str] = None
    VERTEX_LOCATION: str = "us-central1"
    
    # Persistencia y Rutas
    APP_DATA_DIR: str = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")
    SQLITE_DB_PATH: str = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "history.db")
    DOWNLOADS_PATH: str = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "tmp", "downloads")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

def ensure_secret_token():
    """Genera y persiste un WEBHOOK_SECRET_TOKEN si no existe."""
    if not settings.WEBHOOK_SECRET_TOKEN:
        new_token = secrets.token_hex(32)
        env_path = ".env"
        if os.path.exists(env_path):
            set_key(env_path, "WEBHOOK_SECRET_TOKEN", new_token)
            # Recargar configuración
            load_dotenv(env_path, override=True)
            settings.WEBHOOK_SECRET_TOKEN = new_token
            print(f"🔑 Se ha generado un nuevo WEBHOOK_SECRET_TOKEN y se ha guardado en {env_path}")
        else:
            settings.WEBHOOK_SECRET_TOKEN = new_token
            print("⚠️ Advertencia: No se encontró archivo .env. El token generado solo durará esta sesión.")

# Asegurar que los directorios existan
os.makedirs(settings.APP_DATA_DIR, exist_ok=True)
os.makedirs(settings.DOWNLOADS_PATH, exist_ok=True)

# Ejecutar validación de token al importar
ensure_secret_token()
