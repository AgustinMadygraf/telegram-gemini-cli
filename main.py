"""
Path: main.py
"""

import uvicorn
import asyncio
import sys
from src.infrastructure.setting.config import settings
from src.infrastructure.setting.logger import setup_logger
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.interface_adapters.gateways.telegram_gateway import TelegramAdapter
from src.interface_adapters.controllers.telegram_controller import TelegramController
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.infrastructure.fastapi.app import create_app
from src.infrastructure.shell.asyncio_runner import AsyncioShellRunner
from src.infrastructure.shell.local_filesystem import LocalFileSystem
from src.infrastructure.shell.port_guard import PortGuard
from src.infrastructure.shell.cloudflare_runner import CloudflareTunnelRunner
import atexit
from src.use_cases.process_message import ProcessMessageUseCase
from src.use_cases.system_validator import SystemValidatorService

# 0. Configurar Observabilidad
setup_logger()

# 1. Instanciar Infraestructura de Bajo Nivel (OS)
shell_runner = AsyncioShellRunner()
file_system = LocalFileSystem()

# 2. Instanciar Adaptadores de Infraestructura (Gateways)
gemini_gateway = GeminiCLIAdapter(
    shell=shell_runner, 
    fs=file_system,
    binary_path=settings.GEMINI_BINARY_PATH
)
telegram_gateway = TelegramAdapter(token=settings.TELEGRAM_BOT_TOKEN)
tunnel_runner = CloudflareTunnelRunner(
    tunnel_name="gemini-bridge", 
    local_url="http://localhost:8000"
)

# Garantizar cierre del túnel al salir
atexit.register(tunnel_runner.stop_tunnel)

# --- USE CASES ---
validator_service = SystemValidatorService(
    validators=[gemini_gateway, telegram_gateway],
    messenger=telegram_gateway,
    tunnel=tunnel_runner,
    webhook_url=settings.WEBHOOK_URL,
    secret_token=settings.WEBHOOK_SECRET_TOKEN
)

# 2. Instanciar Casos de Uso y Servicios
telegram_presenter = TelegramPresenter()

process_message_use_case = ProcessMessageUseCase(
    ai_engine=gemini_gateway,
    messenger=telegram_gateway,
    presenter=telegram_presenter,
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
    """Realiza las validaciones de inicio, loguea resultados y detiene el sistema si fallan."""
    import logging
    logger = logging.getLogger(__name__)
    
    report = await validator_service.validate_all()
    
    # Procesar mensajes del reporte (Infraestructura decide cómo mostrarlos)
    for msg in report.info_messages:
        logger.info(msg)
    for msg in report.error_messages:
        logger.error(msg)
    for msg in report.critical_messages:
        logger.critical(msg)
        
    if not report.is_ok:
        sys.exit(1)

if __name__ == "__main__":
    # 0. Limpiar puerto si es necesario
    PortGuard(port=8000).clean_port()

    # 1. Iniciar Túnel de Red
    tunnel_runner.start_tunnel()

    # 2. Ejecutar validaciones antes de iniciar el servidor
    asyncio.run(startup_check())
    
    # 3. Correr servidor
    uvicorn.run(app, host="0.0.0.0", port=8000)
