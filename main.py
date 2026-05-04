"""
Path: main.py
"""

import uvicorn
import logging
import sys
import os
from src.infrastructure.setting.config import settings
from src.infrastructure.setting.logger import setup_logger, StandardLoggerAdapter
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.interface_adapters.gateways.telegram_gateway import TelegramAdapter
from src.interface_adapters.controllers.telegram_controller import TelegramController
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.interface_adapters.gateways.mcp_validator_adapter import MCPValidatorAdapter
from src.infrastructure.fastapi.app import create_app
from src.infrastructure.shell.asyncio_runner import AsyncioShellRunner
from src.infrastructure.shell.local_filesystem import LocalFileSystem
from src.infrastructure.shell.port_guard import PortGuard
from src.infrastructure.shell.cloudflare_runner import CloudflareTunnelRunner
from src.infrastructure.markdown.markdown_adapter import PythonMarkdownAdapter
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.use_cases.process_message import ProcessMessageUseCase
from src.use_cases.system_validator import SystemValidatorService
from src.use_cases.services.resilience_service import CircuitBreakerService

import argparse

# 0. Configurar Argumentos de CLI
parser = argparse.ArgumentParser(description="Telegram Gemini Bridge")
parser.add_argument("--debug", action="store_true", help="Activar modo de depuración detallado")
args_cli, _ = parser.parse_known_args() # Usamos parse_known_args para evitar conflictos con uvicorn

# 0.1 Configurar Observabilidad Global
setup_logger()
system_logger = StandardLoggerAdapter("system")
shell_logger = StandardLoggerAdapter("infrastructure.shell")
ai_logger = StandardLoggerAdapter("interface.gemini")
telegram_logger = StandardLoggerAdapter("interface.telegram")
tunnel_logger = StandardLoggerAdapter("infrastructure.tunnel")

# Ajustar niveles según flags de CLI
log_level = logging.DEBUG if args_cli.debug else logging.INFO
shell_logger.logger.setLevel(log_level)
ai_logger.logger.setLevel(log_level)
if args_cli.debug:
    system_logger.logger.setLevel(logging.DEBUG)
    telegram_logger.logger.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ejecutar el Deep Health Check dentro del mismo loop de uvicorn
    if not await startup_check():
        # Usamos os._exit(1) para un cierre inmediato y limpio sin traceback de Starlette
        os._exit(1)
    yield
    # 2. Shutdown
    system_logger.info("🛑 Apagando sistema de forma segura...")
    tunnel_runner.stop_tunnel()

from src.use_cases.services.output_sanitizer import OutputSanitizerService
from src.use_cases.services.credential_manager import CredentialSyncService
from src.use_cases.services.attachment_manager import AttachmentManager
from src.use_cases.services.command_dispatcher import CommandDispatcher
from src.infrastructure.sqlite3.sqlite_history import SQLiteHistoryAdapter
from src.interface_adapters.gateways.gemini_config_adapter import GeminiLocalConfigAdapter

# 1. Instanciar Infraestructura de Bajo Nivel (OS)
shell_runner = AsyncioShellRunner(logger=shell_logger)
file_system = LocalFileSystem()
sanitizer = OutputSanitizerService()
history_adapter = SQLiteHistoryAdapter(
    db_path=settings.SQLITE_DB_PATH, 
    logger=StandardLoggerAdapter("infrastructure.database")
)
circuit_breaker = CircuitBreakerService(failure_threshold=3, recovery_timeout=60)

# 1.1 Servicios de Dominio / Soporte
credential_manager = CredentialSyncService(fs=file_system, logger=ai_logger)
config_provider = GeminiLocalConfigAdapter(fs=file_system, logger=ai_logger)
attachment_manager = AttachmentManager(file_gateway=telegram_adapter, logger=ai_logger, download_path=settings.DOWNLOADS_PATH)
command_dispatcher = CommandDispatcher(ai_engine=gemini_gateway, messenger=telegram_adapter, logger=ai_logger)

# 2. Instanciar Adaptadores de Infraestructura (Gateways)
gemini_gateway = GeminiCLIAdapter(
    shell=shell_runner, 
    fs=file_system,
    logger=ai_logger,
    sanitizer=sanitizer,
    credential_service=credential_manager,
    config_gateway=config_provider,
    binary_path=settings.GEMINI_BINARY_PATH,
    auth_method=settings.GEMINI_AUTH_METHOD,
    api_key=settings.GEMINI_API_KEY,
    vertex_project=settings.VERTEX_PROJECT_ID,
    vertex_location=settings.VERTEX_LOCATION,
    workspace_path=settings.GEMINI_WORKSPACE
)

telegram_adapter = TelegramAdapter(
    token=settings.TELEGRAM_BOT_TOKEN, 
    logger=telegram_logger
)

tunnel_runner = CloudflareTunnelRunner(
    tunnel_name="gemini-bridge", 
    local_url="http://localhost:8000",
    logger=tunnel_logger
)
mcp_validator = MCPValidatorAdapter(fs=file_system, ai_engine=gemini_gateway)

# 3. Instanciar Casos de Uso y Servicios
validator_service = SystemValidatorService(
    validators=[gemini_gateway, telegram_adapter],
    logger=system_logger,
    messenger=telegram_adapter, # Implementa MessageGateway
    web_admin=telegram_adapter, # Implementa WebAdminGateway
    tunnel=tunnel_runner,
    mcp_validator=mcp_validator,
    webhook_url=settings.WEBHOOK_URL,
    secret_token=settings.WEBHOOK_SECRET_TOKEN,
    admin_chat_id=settings.ALLOWED_CHAT_IDS[0] if settings.ALLOWED_CHAT_IDS else None
)

markdown_converter = PythonMarkdownAdapter()
telegram_presenter = TelegramPresenter(
    markdown_converter=markdown_converter,
    logger=StandardLoggerAdapter("interface.presenter")
)

process_message_use_case = ProcessMessageUseCase(
    ai_engine=gemini_gateway, 
    messenger=telegram_adapter, 
    presenter=telegram_presenter,
    logger=StandardLoggerAdapter("use_case.process_message"),
    allowed_users=settings.ALLOWED_CHAT_IDS,
    attachment_manager=attachment_manager,
    command_dispatcher=command_dispatcher,
    history=history_adapter,
    circuit_breaker=circuit_breaker
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

async def startup_check() -> bool:
    """Delegación del Deep Health Check al servicio de validación."""
    system_logger.info("🔍 Iniciando Deep Health Check")
    
    try:
        report = await validator_service.validate_all()
        if not report.is_ok:
            system_logger.critical("❌ El sistema no superó el Deep Health Check. Abortando.")
            return False
        return True
    except Exception as e:
        system_logger.critical(f"💥 Fallo inesperado durante la validación: {e}")
        return False
    
    system_logger.info("🚀 Sistema listo para recibir mensajes.")

if __name__ == "__main__":
    os.system('clear')
    os.system('clear')
    # Restaurar TTY al inicio por si quedó corrupto de una sesión previa
    if sys.stdout.isatty():
        os.system('stty sane')
    
    try:
        PortGuard(port=8000, logger=system_logger).clean_port()
        tunnel_runner.start_tunnel()
        
        # Arrancamos uvicorn directamente; el lifespan se encargará del check
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        pass
    finally:
        system_logger.info("👋 ¡Hasta luego!")
