"""
Path: src/use_cases/process_message.py
"""

from src.use_cases.ports.interfaces import (
    AIEngineGateway, 
    MessageGateway,
    FileGateway,
    MessagePresenter,
    ChatHistoryGateway,
    LoggerPort
)
from src.entities.chat import ChatMessage
from src.entities.ai import AIResponse
from src.entities.ai_session import AISession
from src.use_cases.services.resilience_service import CircuitBreakerService
from typing import List, Optional
import os

class ProcessMessageUseCase:
    def __init__(
        self, 
        ai_engine: AIEngineGateway, 
        messenger: MessageGateway,
        presenter: MessagePresenter,
        logger: LoggerPort,
        allowed_users: List[int],
        history: Optional[ChatHistoryGateway] = None,
        file_gateway: Optional[FileGateway] = None,
        circuit_breaker: Optional[CircuitBreakerService] = None
    ):
        self.ai_engine = ai_engine
        self.messenger = messenger
        self.file_gateway = file_gateway
        self.presenter = presenter
        self.logger = logger
        self.allowed_users = allowed_users
        self.history = history
        self.circuit_breaker = circuit_breaker or CircuitBreakerService()

    async def validate_user(self, user_id: int, chat_id: int) -> None:
        if user_id not in self.allowed_users:
            await self.messenger.send_message(
                chat_id, 
                f"⚠️ <b>Acceso denegado</b>\nSu ID de usuario (<code>{user_id}</code>) no está autorizado. Contacte con el administrador.",
                parse_mode="HTML"
            )
            raise PermissionError(f"User {user_id} not in whitelist")

    async def execute(self, message: ChatMessage) -> None:
        await self.validate_user(message.user_id, message.chat_id)

        # 0. Persistir mensaje del usuario
        session_id = f"chat_{message.chat_id}"
        if self.history:
            message.role = "user"
            message.session_id = session_id
            await self.history.save_message(message)

        # 1. Manejo de Comandos Especiales
        session = AISession(id=session_id)
        if message.text.strip().lower() == "/reset":
            await self.messenger.set_typing(message.chat_id)
            success = await self.ai_engine.reset(session=session)
            await self.messenger.send_message(
                chat_id=message.chat_id, 
                text="🔄 <b>Contexto reiniciado</b>" if success else "❌ <b>Error al reiniciar</b>",
                parse_mode="HTML"
            )
            return

        # 2. Verificar Circuit Breaker antes de proceder
        if not self.circuit_breaker.can_execute():
            self.logger.warning(f"🛡️ Circuito ABIERTO para chat {message.chat_id}. Rechazando ejecución.")
            await self.messenger.send_message(
                chat_id=message.chat_id,
                text="🛡️ <b>Modo de Resiliencia Activo</b>\nEstoy experimentando fallos técnicos persistentes y he entrado en modo de autoprotección. Por favor, intenta de nuevo en un minuto.",
                parse_mode="HTML"
            )
            return

        # 3. Notificar estado (Typing)
        await self.messenger.set_typing(message.chat_id)
        
        # 4. Manejo de Adjuntos (Multimodal)
        attachments = []
        if message.photo_ids and self.file_gateway:
            for photo_id in message.photo_ids:
                file_path = await self.file_gateway.get_file_path(photo_id)
                if file_path:
                    from src.infrastructure.setting.config import settings
                    local_filename = f"photo_{photo_id}.jpg"
                    local_path = os.path.join(settings.DOWNLOADS_PATH, local_filename)
                    if await self.file_gateway.download_file(file_path, local_path):
                        attachments.append(local_path)

        # 5. Consultar a la IA con Circuit Breaker
        try:
            response = await self.ai_engine.ask(message.text, session=session, attachments=attachments)
            
            if response.success and response.text.strip():
                self.circuit_breaker.record_success()
            else:
                self.circuit_breaker.record_failure()
                if not response.text.strip():
                    response.success = False
                    response.error_message = "Respuesta vacía tras sanitización"
        except Exception as e:
            self.circuit_breaker.record_failure()
            response = AIResponse(text="", success=False, error_message=str(e))

        # 6. Limpieza y Persistencia
        for path in attachments:
            try: os.remove(path)
            except: pass
        
        if response.success:
            self.logger.info(f"📤 [OUT] Gemini: \"{response.text[:60]}...\"")
            if self.history:
                ai_msg = ChatMessage(chat_id=message.chat_id, user_id=0, text=response.text, role="assistant", session_id=session_id)
                await self.history.save_message(ai_msg)
        else:
            self.logger.error(f"⚠️ [ERR] Gemini falló: {response.error_message}")
            response.text = "❌ <b>Error Técnico</b>\nEstoy experimentando dificultades. Por favor, intenta de nuevo."

        # 7. Formatear y Enviar
        formatted_messages = self.presenter.format_response(response)
        for msg_text in formatted_messages:
            await self.messenger.send_message(chat_id=message.chat_id, text=msg_text, parse_mode="HTML")
