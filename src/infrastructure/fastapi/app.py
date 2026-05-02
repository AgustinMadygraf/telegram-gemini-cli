"""
Path: src/infrastructure/fastapi/app.py
"""

import logging
from fastapi import FastAPI, Request, BackgroundTasks, Header, HTTPException
from src.interface_adapters.controllers.telegram_controller import TelegramController

logger = logging.getLogger(__name__)

def create_app(controller: TelegramController):
    app = FastAPI(title="Telegram Gemini CLI Bridge")

    @app.post("/webhook")
    async def webhook_route(
        request: Request, 
        background_tasks: BackgroundTasks,
        x_telegram_bot_api_secret_token: str = Header(None)
    ):
        try:
            # 1. Obtener JSON crudo
            data = await request.json()
            
            # 2. Delegar procesamiento al controlador (Capa Interface Adapters)
            chat_message = await controller.process_webhook_data(
                data, 
                x_telegram_bot_api_secret_token
            )
            
            # 3. Si hay un mensaje válido, agendar ejecución asíncrona
            if chat_message:
                background_tasks.add_task(controller.execute_task, chat_message)
            
            return {"status": "ok"}

        except PermissionError:
            # La infraestructura decide loguear el fallo de seguridad
            logger.warning("Intento de webhook con token secreto inválido interceptado en la ruta.")
            raise HTTPException(status_code=403, detail="Forbidden")
        except Exception as e:
            logger.error(f"Error no controlado en el webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
