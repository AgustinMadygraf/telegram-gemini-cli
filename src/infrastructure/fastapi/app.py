"""
Path: src/infrastructure/fastapi/app.py
"""

from fastapi import FastAPI, Request, BackgroundTasks
from src.interface_adapters.controllers.telegram_controller import TelegramController

def create_app(controller: TelegramController):
    app = FastAPI(title="Telegram Gemini CLI Bridge")

    @app.post("/webhook")
    async def webhook_route(
        request: Request, 
        background_tasks: BackgroundTasks,
        x_telegram_bot_api_secret_token: str = None
    ):
        # Delegamos la lógica al controlador
        return await controller.handle_webhook(
            request, 
            background_tasks, 
            x_telegram_bot_api_secret_token
        )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
