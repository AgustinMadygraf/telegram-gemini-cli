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

    async def handle_webhook(self, data: dict, x_telegram_bot_api_secret_token: str = None):
        """Punto de entrada para los webhooks de Telegram."""
        from src.infrastructure.setting.logger import correlation_id
        import uuid
        
        # Generar un ID de rastreo único para esta petición
        trace_id = f"TR-{uuid.uuid4().hex[:6]}"
        correlation_id.set(trace_id)
        
        # 1. Validar Token
        if self.secret_token and x_telegram_bot_api_secret_token != self.secret_token:
            raise PermissionError("Invalid secret token")

        # 2. Extraer ChatMessage
        if "message" in data:
            msg_data = data["message"]
            text = msg_data.get("text") or msg_data.get("caption", "")
            
            photo_ids = []
            if "photo" in msg_data:
                photo_ids.append(msg_data["photo"][-1]["file_id"])
            
            if not text and not photo_ids:
                return None

            msg = ChatMessage(
                chat_id=msg_data["chat"]["id"],
                user_id=msg_data["from"]["id"],
                text=text,
                username=msg_data["from"].get("username"),
                photo_ids=photo_ids if photo_ids else None
            )
            
            await self.use_case.validate_user(msg.user_id, msg.chat_id)
            
            # Devolvemos el mensaje y el ID de rastreo para la tarea de fondo
            return msg, trace_id
        
        return None, None

    async def execute_task(self, chat_message: ChatMessage, trace_id: str):
        """Mantiene el desacoplamiento para la ejecución diferida con rastreo."""
        from src.infrastructure.setting.logger import correlation_id
        correlation_id.set(trace_id)
        await self.use_case.execute(chat_message)
