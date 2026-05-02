"""
Path: src/interface_adapters/controllers/telegram_controller.py
"""

from src.use_cases.process_message import ProcessMessageUseCase
from src.entities.chat import ChatMessage
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TelegramController:
    def __init__(self, use_case: ProcessMessageUseCase, secret_token: str):
        self.use_case = use_case
        self.secret_token = secret_token

    async def process_webhook_data(self, data: Dict[str, Any], x_token: Optional[str]) -> Optional[ChatMessage]:
        """
        Valida el secreto y extrae el mensaje del payload de Telegram.
        No conoce a FastAPI.
        """
        # 1. Validar Token
        if self.secret_token and x_token != self.secret_token:
            logger.warning("Intento de webhook con token secreto inválido")
            raise PermissionError("Invalid secret token")

        # 2. Extraer ChatMessage
        if "message" in data and "text" in data["message"]:
            msg_data = data["message"]
            return ChatMessage(
                chat_id=msg_data["chat"]["id"],
                user_id=msg_data["from"]["id"],
                text=msg_data["text"],
                username=msg_data["from"].get("username")
            )
        
        return None

    async def execute_task(self, chat_message: ChatMessage):
        """Mantiene el desacoplamiento para la ejecución diferida."""
        await self.use_case.execute(chat_message)
