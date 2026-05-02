"""
Path: main.py
"""

import uvicorn
import asyncio
import sys
from src.infrastructure.setting.config import settings
from src.infrastructure.setting.logger import setup_logger
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.interface_adapters.gateways.telegram_gateway import TelegramAdapter
from src.interface_adapters.controllers.telegram_controller import TelegramController
from src.infrastructure.fastapi.app import create_app
from src.use_cases.process_message import ProcessMessageUseCase
from src.use_cases.system_validator import SystemValidatorService

# 0. Configurar Observabilidad
setup_logger()

# 1. Instanciar Adaptadores de Infraestructura (Gateways)
gemini_gateway = GeminiCLIAdapter(binary_path=settings.GEMINI_BINARY_PATH)
telegram_gateway = TelegramAdapter(token=settings.TELEGRAM_BOT_TOKEN)

# 2. Instanciar Casos de Uso y Servicios
validator_service = SystemValidatorService(
    validators=[gemini_gateway, telegram_gateway],
    messenger=telegram_gateway,
    webhook_url=settings.WEBHOOK_URL,
    secret_token=settings.WEBHOOK_SECRET_TOKEN
)

process_message_use_case = ProcessMessageUseCase(
    ai_engine=gemini_gateway,
    messenger=telegram_gateway,
    allowed_users=settings.ALLOWED_CHAT_IDS
)

# 3. Instanciar Adaptadores de Interfaz (Controllers)
telegram_controller = TelegramController(
    use_case=process_message_use_case,
    secret_token=settings.WEBHOOK_SECRET_TOKEN
)

# 4. Crear App de FastAPI (Infraestructura)
app = create_app(controller=telegram_controller)

async def startup_check():
    """Realiza las validaciones de inicio y detiene el sistema si fallan."""
    if not await validator_service.validate_all():
        import logging
        logger = logging.getLogger(__name__)
        logger.critical("Fallo crítico en la validación del sistema. El proceso se detendrá.")
        sys.exit(1)

if __name__ == "__main__":
    # Ejecutar validaciones antes de iniciar el servidor
    asyncio.run(startup_check())
    
    # Correr servidor
    uvicorn.run(app, host="0.0.0.0", port=8000)
