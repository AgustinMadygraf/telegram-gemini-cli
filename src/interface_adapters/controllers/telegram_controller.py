from fastapi import Request, BackgroundTasks, Header, HTTPException
from src.use_cases.process_message import ProcessMessageUseCase
from src.entities.chat import ChatMessage
import logging

logger = logging.getLogger(__name__)

class TelegramController:
    def __init__(self, use_case: ProcessMessageUseCase, secret_token: str):
        self.use_case = use_case
        self.secret_token = secret_token

    async def handle_webhook(
        self, 
        request: Request, 
        background_tasks: BackgroundTasks,
        x_telegram_bot_api_secret_token: str = Header(None)
    ):
        if self.secret_token and x_telegram_bot_api_secret_token != self.secret_token:
            logger.warning("Intento de webhook con token secreto inválido")
            raise HTTPException(status_code=403, detail="Forbidden")

        data = await request.json()
        
        if "message" in data and "text" in data["message"]:
            msg_data = data["message"]
            chat_message = ChatMessage(
                chat_id=msg_data["chat"]["id"],
                user_id=msg_data["from"]["id"],
                text=msg_data["text"],
                username=msg_data["from"].get("username")
            )
            
            background_tasks.add_task(self.use_case.execute, chat_message)

        return {"status": "ok"}
