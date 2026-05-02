import uvicorn
import logging
import asyncio
import sys
from config.settings import settings
from src.infrastructure.adapters.gemini_adapter import GeminiCLIAdapter
from src.infrastructure.adapters.telegram_adapter import TelegramAdapter
from src.infrastructure.adapters.fastapi_adapter import create_app
from src.application.process_message import ProcessMessageUseCase
from src.application.system_validator import SystemValidatorService

# 0. Configurar Observabilidad (Logging)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# 1. Instanciar Adaptadores de Infraestructura
gemini_engine = GeminiCLIAdapter(binary_path=settings.GEMINI_BINARY_PATH)
messenger = TelegramAdapter(token=settings.TELEGRAM_BOT_TOKEN)

# 2. Instanciar Servicios y Casos de Uso (Inyección de Dependencias)
validator_service = SystemValidatorService(validators=[gemini_engine, messenger])

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

async def startup_check():
    """Realiza las validaciones de inicio y detiene el sistema si fallan."""
    if not await validator_service.validate_all():
        logger.critical("Fallo crítico en la validación del sistema. El proceso se detendrá.")
        sys.exit(1)

if __name__ == "__main__":
    # Ejecutar validaciones antes de iniciar el servidor
    asyncio.run(startup_check())
    
    # Correr servidor
    uvicorn.run(app, host="0.0.0.0", port=8000)
