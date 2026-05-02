"""
Path: src/interface_adapters/controllers/telegram_controller.py
"""

from src.use_cases.process_message import ProcessMessageUseCase
from src.entities.chat import ChatMessage
from typing import Optional, Dict, Any


class TelegramController:
    def __init__(self, use_case: ProcessMessageUseCase, secret_token: str):
        self.use_case = use_case
        self.secret_token = secret_token

    async def process_webhook_data(self, data: Dict[str, Any], x_token: Optional[str]) -> Optional[ChatMessage]:
        # 1. Validar Token
        if self.secret_token and x_token != self.secret_token:
            # El controlador solo lanza la excepción, no loguea.
            raise PermissionError("Invalid secret token")

        # 2. Extraer ChatMessage
        if "message" in data and "text" in data["message"]:
            msg_data = data["message"]
            msg = ChatMessage(
                chat_id=msg_data["chat"]["id"],
                user_id=msg_data["from"]["id"],
                text=msg_data["text"],
                username=msg_data["from"].get("username")
            )
            
            # 3. Validar Usuario (Lanza PermissionError si no está en whitelist)
            await self.use_case.validate_user(msg.user_id, msg.chat_id)
            
            return msg
        
        return None

    async def execute_task(self, chat_message: ChatMessage):
        """Mantiene el desacoplamiento para la ejecución diferida."""
        await self.use_case.execute(chat_message)
