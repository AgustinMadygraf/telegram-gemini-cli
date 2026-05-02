"""
Path: src/use_cases/process_message.py
"""

from src.entities.chat import ChatMessage
from src.use_cases.ports.interfaces import (
    AIEngineGateway, 
    MessengerGateway, 
    MessagePresenter
)
from typing import List

class ProcessMessageUseCase:
    def __init__(
        self, 
        ai_engine: AIEngineGateway, 
        messenger: MessengerGateway,
        presenter: MessagePresenter,
        allowed_users: List[int]
    ):
        self.ai_engine = ai_engine
        self.messenger = messenger
        self.presenter = presenter
        self.allowed_users = allowed_users

    def validate_user(self, user_id: int) -> None:
        if user_id not in self.allowed_users:
            raise PermissionError(f"User {user_id} not in whitelist")

    async def execute(self, message: ChatMessage) -> None:
        self.validate_user(message.user_id)

        # 1. Notificar estado (Typing)
        await self.messenger.set_typing(message.chat_id)
        
        # 2. Consultar a la IA
        response = await self.ai_engine.ask(message.text)
        
        # 3. Formatear respuesta vía Presenter (Capa de Presentación)
        # El presenter se encarga de escapar MarkdownV2 y fragmentar si es largo.
        formatted_messages = self.presenter.format_response(response)

        # 4. Enviar cada fragmento resultante
        for msg_text in formatted_messages:
            await self.messenger.send_message(
                chat_id=message.chat_id, 
                text=msg_text,
                parse_mode="MarkdownV2"
            )
