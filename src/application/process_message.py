from src.domain.entities import ChatMessage
from src.domain.interfaces import AIEngineInterface, MessagingProviderInterface
from typing import List

class ProcessMessageUseCase:
    def __init__(
        self, 
        ai_engine: AIEngineInterface, 
        messenger: MessagingProviderInterface,
        allowed_users: List[int]
    ):
        self.ai_engine = ai_engine
        self.messenger = messenger
        self.allowed_users = allowed_users

    async def execute(self, message: ChatMessage) -> None:
        # 1. Autorización básica
        if message.user_id not in self.allowed_users:
            await self.messenger.send_message(
                message.chat_id, 
                "Lo siento, no tienes permiso para usar este bot."
            )
            return

        # 2. Feedback visual
        await self.messenger.set_typing(message.chat_id)

        # 3. Procesamiento con IA
        response = await self.ai_engine.ask(message.text)

        # 4. Respuesta al usuario
        if response.success:
            await self.messenger.send_message(message.chat_id, response.text)
        else:
            await self.messenger.send_message(
                message.chat_id, 
                f"Error al procesar: {response.error_message}"
            )
