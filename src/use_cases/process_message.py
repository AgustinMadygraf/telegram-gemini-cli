from src.entities.chat import ChatMessage
from src.use_cases.ports.interfaces import AIEngineGateway, MessengerGateway
from typing import List

class ProcessMessageUseCase:
    def __init__(
        self, 
        ai_engine: AIEngineGateway, 
        messenger: MessengerGateway,
        allowed_users: List[int]
    ):
        self.ai_engine = ai_engine
        self.messenger = messenger
        self.allowed_users = allowed_users

    async def execute(self, message: ChatMessage) -> None:
        if message.user_id not in self.allowed_users:
            await self.messenger.send_message(
                message.chat_id, 
                "Lo siento, no tienes permiso para usar este bot."
            )
            return

        await self.messenger.set_typing(message.chat_id)
        response = await self.ai_engine.ask(message.text)

        if response.success:
            await self.messenger.send_message(message.chat_id, response.text)
        else:
            await self.messenger.send_message(
                message.chat_id, 
                f"Error al procesar: {response.error_message}"
            )
