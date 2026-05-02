"""
Path: src/infrastructure/fastapi/app.py
"""

from fastapi import FastAPI, Request, BackgroundTasks, Header
from typing import Optional, Any
from src.interface_adapters.controllers.telegram_controller import TelegramController
from src.infrastructure.fastapi.middleware import ObservabilityMiddleware

def create_app(controller: TelegramController, lifespan: Optional[Any] = None) -> FastAPI:
    app = FastAPI(
        title="Telegram Gemini CLI Bridge",
        lifespan=lifespan
    )

    # Añadir Middleware de Observabilidad
    app.add_middleware(ObservabilityMiddleware)

    @app.post("/webhook")
    async def webhook_route(
        request: Request, 
        background_tasks: BackgroundTasks,
        x_telegram_bot_api_secret_token: str = Header(None)
    ):
        # 1. Obtener JSON crudo
        data = await request.json()
        
        # 2. Delegar procesamiento al controlador
        # Si el token es inválido, lanzará PermissionError y el Middleware lo capturará
        chat_message = await controller.process_webhook_data(
            data, 
            x_telegram_bot_api_secret_token
        )
        
        # 3. Agendar ejecución asíncrona
        if chat_message:
            background_tasks.add_task(controller.execute_task, chat_message)
        
        return {"status": "ok"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
