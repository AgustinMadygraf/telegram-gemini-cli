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
from fastapi import FastAPI
from contextlib import asynccontextmanager
import atexit
from src.use_cases.process_message import ProcessMessageUseCase
from src.use_cases.system_validator import SystemValidatorService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ejecutar validaciones dentro del loop de FastAPI
    await startup_check()
    yield
    # Cleanup si fuera necesario (atexit ya maneja el túnel)

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

# 4. Crear Aplicación FastAPI
app = create_app(
    controller=telegram_controller,
    lifespan=lifespan
)

async def startup_check():
    """Delegación del Deep Health Check al servicio de validación."""
    report = await validator_service.validate_all()
    
    # Procesar resultados según el reporte
    for msg in report.info_messages:
        print(f"✅ {msg}")
    for msg in report.error_messages:
        print(f"⚠️  Error: {msg}")
    for msg in report.critical_messages:
        print(f"❌ CRÍTICO: {msg}")

    if not report.is_ok:
        sys.exit(1)

if __name__ == "__main__":
    # 0. Limpiar puerto si es necesario
    PortGuard(port=8000).clean_port()

    # 1. Iniciar Túnel de Red
    tunnel_runner.start_tunnel()

    # 2. Correr servidor (El lifespan se encargará del startup_check)
    uvicorn.run(app, host="0.0.0.0", port=8000)
