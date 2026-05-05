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
from src.use_cases.services.attachment_manager import AttachmentManager
from src.use_cases.services.command_dispatcher import CommandDispatcher
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
        attachment_manager: AttachmentManager,
        command_dispatcher: CommandDispatcher,
        history: Optional[ChatHistoryGateway] = None,
        circuit_breaker: Optional[CircuitBreakerService] = None
    ):
        self.ai_engine = ai_engine
        self.messenger = messenger
        self.presenter = presenter
        self.logger = logger
        self.allowed_users = allowed_users
        self.attachments = attachment_manager
        self.commands = command_dispatcher
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

        # 0. Preparar sesión
        session_id = f"chat_{message.chat_id}"
        session = AISession(id=session_id)
        
        # 1. Persistencia inicial (Historial)
        if self.history:
            message.role = "user"
            message.session_id = session_id
            await self.history.save_message(message)

        # 2. Manejo de Comandos (Delegado)
        if await self.commands.is_command(message.text):
            if await self.commands.dispatch(message.text, message.chat_id, session):
                return

        # 3. Guardián de Resiliencia
        if not self.circuit_breaker.can_execute():
            await self.messenger.send_message(
                chat_id=message.chat_id,
                text="🛡️ <b>Modo de Resiliencia Activo</b>\nEstoy experimentando fallos técnicos. Reintenta en 1 minuto.",
                parse_mode="HTML"
            )
            return

        # 4. Procesamiento de Mensaje
        await self.messenger.set_typing(message.chat_id)
        
        local_attachments = []
        try:
            # 4.1 Descargar adjuntos (Delegado)
            if message.photo_ids:
                local_attachments = await self.attachments.download_attachments(message.photo_ids)

            # 4.2 Obtener contexto histórico si está habilitado
            history_context = []
            if self.history:
                history_context = await self.history.get_recent_history(message.chat_id, limit=10)
                # Omitir el último mensaje (que es el actual y ya se guardó arriba) para no duplicar
                if history_context and history_context[-1].text == message.text:
                    history_context.pop()

            # 4.3 Consultar a la IA
            response = await self.ai_engine.ask(
                message.text, 
                history=history_context, 
                session=session, 
                attachments=local_attachments
            )
            
            # 4.3 Registrar resultado en Circuit Breaker
            if response.success and response.text.strip():
                self.circuit_breaker.record_success()
            else:
                self.circuit_breaker.record_failure()
                if not response.text.strip():
                    response.success = False
                    response.error_message = "Respuesta vacía tras sanitización"

            # 5. Persistencia y Respuesta
            if response.success:
                self.logger.info(f"📤 [OUT] Gemini: \"{response.text[:60]}...\"")
                if self.history:
                    ai_msg = ChatMessage(chat_id=message.chat_id, user_id=0, text=response.text, role="assistant", session_id=session_id)
                    await self.history.save_message(ai_msg)
            else:
                self.logger.error(f"⚠️ [ERR] Gemini falló: {response.error_message}")
                response.text = "❌ <b>Error Técnico</b>\nEstoy experimentando dificultades. Reintenta en breve."

            # 6. Formatear y Enviar (Presentación)
            formatted_messages = self.presenter.format_response(response)
            for msg_text in formatted_messages:
                await self.messenger.send_message(chat_id=message.chat_id, text=msg_text, parse_mode="HTML")

        except Exception as e:
            self.circuit_breaker.record_failure()
            self.logger.error(f"💥 Error fatal en Use Case: {e}")
            await self.messenger.send_message(message.chat_id, "💥 Ocurrió un error inesperado.")
        finally:
            # 7. Limpieza (Delegado)
            self.attachments.cleanup(local_attachments)
