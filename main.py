import uvicorn
from config.settings import settings
from src.infrastructure.adapters.gemini_adapter import GeminiCLIAdapter
from src.infrastructure.adapters.telegram_adapter import TelegramAdapter
from src.infrastructure.adapters.fastapi_adapter import create_app
from src.application.process_message import ProcessMessageUseCase

# 1. Instanciar Adaptadores de Infraestructura
gemini_engine = GeminiCLIAdapter(binary_path=settings.GEMINI_BINARY_PATH)
messenger = TelegramAdapter(token=settings.TELEGRAM_BOT_TOKEN)

# 2. Instanciar Caso de Uso (Inyección de Dependencias)
process_message_use_case = ProcessMessageUseCase(
    ai_engine=gemini_engine,
    messenger=messenger,
    allowed_users=settings.ALLOWED_CHAT_IDS
)

# 3. Crear App de FastAPI
app = create_app(
    use_case=process_message_use_case, 
    secret_token=settings.WEBHOOK_SECRET_TOKEN
)

if __name__ == "__main__":
    # Correr servidor
    uvicorn.run(app, host="0.0.0.0", port=8000)
