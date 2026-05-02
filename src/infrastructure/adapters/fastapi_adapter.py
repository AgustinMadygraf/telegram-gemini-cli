from fastapi import FastAPI, Request, BackgroundTasks, Header, HTTPException
from src.application.process_message import ProcessMessageUseCase
from src.domain.entities import ChatMessage
import logging

logger = logging.getLogger(__name__)

def create_app(use_case: ProcessMessageUseCase, secret_token: str):
    app = FastAPI()

    @app.post("/webhook")
    async def webhook(
        request: Request, 
        background_tasks: BackgroundTasks,
        x_telegram_bot_api_secret_token: str = Header(None)
    ):
        # Validar el token secreto si está configurado
        if secret_token and x_telegram_bot_api_secret_token != secret_token:
            logger.warning("Intento de webhook con token secreto inválido")
            raise HTTPException(status_code=403, detail="Forbidden")

        data = await request.json()
        
        # Parsear el mensaje básico de Telegram
        if "message" in data and "text" in data["message"]:
            msg_data = data["message"]
            chat_message = ChatMessage(
                chat_id=msg_data["chat"]["id"],
                user_id=msg_data["from"]["id"],
                text=msg_data["text"],
                username=msg_data["from"].get("username")
            )
            
            # Ejecutar el caso de uso en segundo plano para responder 200 OK rápido
            background_tasks.add_task(use_case.execute, chat_message)

        return {"status": "ok"}

    return app
