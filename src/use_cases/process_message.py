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

    async def validate_user(self, user_id: int, chat_id: int) -> None:
        if user_id not in self.allowed_users:
            # Enviar mensaje de cortesía al usuario en Telegram (Usando HTML)
            await self.messenger.send_message(
                chat_id, 
                f"⚠️ <b>Acceso denegado</b>\nSu ID de usuario (<code>{user_id}</code>) no está autorizado. Contacte con el administrador.",
                parse_mode="HTML"
            )
            raise PermissionError(f"User {user_id} not in whitelist")

    async def execute(self, message: ChatMessage) -> None:
        await self.validate_user(message.user_id, message.chat_id)

        # 1. Manejo de Comandos Especiales
        session_id = f"chat_{message.chat_id}"
        if message.text.strip().lower() == "/reset":
            await self.messenger.set_typing(message.chat_id)
            success = await self.ai_engine.reset(session_id=session_id)
            if success:
                await self.messenger.send_message(
                    chat_id=message.chat_id, 
                    text="🔄 <b>Contexto reiniciado</b>\nSe ha limpiado el historial de la conversación.",
                    parse_mode="HTML"
                )
            else:
                await self.messenger.send_message(
                    chat_id=message.chat_id, 
                    text="❌ <b>Error</b>\nNo se pudo reiniciar el contexto.",
                    parse_mode="HTML"
                )
            return

        # 2. Notificar estado (Typing)
        await self.messenger.set_typing(message.chat_id)
        
        # 3. Consultar a la IA
        response = await self.ai_engine.ask(message.text, session_id=session_id)
        
        # 3. Formatear respuesta vía Presenter (Capa de Presentación)
        # El presenter ahora convierte Markdown a HTML robusto.
        formatted_messages = self.presenter.format_response(response)

        # 4. Enviar cada fragmento resultante
        for msg_text in formatted_messages:
            await self.messenger.send_message(
                chat_id=message.chat_id, 
                text=msg_text,
                parse_mode="HTML"
            )
