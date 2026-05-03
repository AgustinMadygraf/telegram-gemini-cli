"""
Path: main.py
"""

import uvicorn
import sys
import os
from src.infrastructure.setting.config import settings
from src.infrastructure.setting.logger import setup_logger
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.interface_adapters.gateways.telegram_gateway import TelegramAdapter
from src.interface_adapters.controllers.telegram_controller import TelegramController
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.interface_adapters.gateways.mcp_validator_adapter import MCPValidatorAdapter
from src.infrastructure.fastapi.app import create_app
from src.infrastructure.setting.logger import setup_logger, StandardLoggerAdapter
from src.infrastructure.shell.asyncio_runner import AsyncioShellRunner
from src.infrastructure.shell.local_filesystem import LocalFileSystem
from src.infrastructure.shell.port_guard import PortGuard
from src.infrastructure.shell.cloudflare_runner import CloudflareTunnelRunner
from src.infrastructure.markdown.markdown_adapter import PythonMarkdownAdapter
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.use_cases.process_message import ProcessMessageUseCase
from src.use_cases.system_validator import SystemValidatorService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup
    await startup_check()
    yield
    # 2. Shutdown
    print("\n🛑 Apagando sistema de forma segura...")
    tunnel_runner.stop_tunnel()

# 0. Configurar Observabilidad Global
setup_logger()
system_logger = StandardLoggerAdapter("system")
shell_logger = StandardLoggerAdapter("infrastructure.shell")
ai_logger = StandardLoggerAdapter("interface.gemini")
telegram_logger = StandardLoggerAdapter("interface.telegram")

from src.use_cases.services.output_sanitizer import OutputSanitizerService

from src.infrastructure.database.sqlite_history import SQLiteHistoryAdapter

# 1. Instanciar Infraestructura de Bajo Nivel (OS)
shell_runner = AsyncioShellRunner(logger=shell_logger)
file_system = LocalFileSystem()
sanitizer = OutputSanitizerService()
history_adapter = SQLiteHistoryAdapter(
    db_path=settings.SQLITE_DB_PATH, 
    logger=StandardLoggerAdapter("infrastructure.database")
)

# 2. Instanciar Adaptadores de Infraestructura (Gateways)
# ... (gemini_gateway instanciado antes)
gemini_gateway = GeminiCLIAdapter(
    shell=shell_runner, 
    fs=file_system,
    logger=ai_logger,
    sanitizer=sanitizer,
    binary_path=settings.GEMINI_BINARY_PATH,
    auth_method=settings.GEMINI_AUTH_METHOD,
    api_key=settings.GEMINI_API_KEY,
    vertex_project=settings.VERTEX_PROJECT_ID,
    vertex_location=settings.VERTEX_LOCATION,
    workspace_path=settings.GEMINI_WORKSPACE
)

telegram_gateway = TelegramAdapter(
    token=settings.TELEGRAM_BOT_TOKEN, 
    logger=telegram_logger
)

tunnel_runner = CloudflareTunnelRunner(
    tunnel_name="gemini-bridge", 
    local_url="http://localhost:8000"
)
mcp_validator = MCPValidatorAdapter(fs=file_system)

# 3. Instanciar Casos de Uso y Servicios
validator_service = SystemValidatorService(
    validators=[gemini_gateway, telegram_gateway],
    logger=system_logger,
    messenger=telegram_gateway,
    tunnel=tunnel_runner,
    mcp_validator=mcp_validator,
    webhook_url=settings.WEBHOOK_URL,
    secret_token=settings.WEBHOOK_SECRET_TOKEN
)

markdown_converter = PythonMarkdownAdapter()
telegram_presenter = TelegramPresenter(
    markdown_converter=markdown_converter,
    logger=StandardLoggerAdapter("interface.presenter")
)

process_message_use_case = ProcessMessageUseCase(
    ai_engine=gemini_gateway,
    messenger=telegram_gateway,
    presenter=telegram_presenter,
    logger=StandardLoggerAdapter("use_case.process_message"),
    allowed_users=settings.ALLOWED_CHAT_IDS,
    history=history_adapter
)

# 4. Instanciar Adaptadores de Interfaz (Controllers)
telegram_controller = TelegramController(
    use_case=process_message_use_case,
    secret_token=settings.WEBHOOK_SECRET_TOKEN
)

# 5. Crear Aplicación FastAPI
app = create_app(
    controller=telegram_controller,
    lifespan=lifespan
)

async def startup_check():
    """Delegación del Deep Health Check al servicio de validación."""
    system_logger.info("🔍 Iniciando Deep Health Check")
    
    report = await validator_service.validate_all()
    
    if not report.is_ok:
        # El validator_service ya habrá logueado los errores a través de su logger inyectado
        sys.exit(1)
    
    system_logger.info("🚀 Sistema listo para recibir mensajes.")

if __name__ == "__main__":
    # Doble limpieza de pantalla para un inicio impecable
    os.system('clear')
    os.system('clear')
    
    try:
        # 0. Limpiar puerto si es necesario
        PortGuard(port=8000).clean_port()

        # 1. Iniciar Túnel de Red
        tunnel_runner.start_tunnel()

        # 2. Correr servidor (El lifespan se encargará del startup_check y cleanup)
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        pass
    finally:
        print("👋 ¡Hasta luego!")
