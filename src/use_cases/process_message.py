"""
Path: src/use_cases/process_message.py
"""

from src.use_cases.ports.interfaces import (
    AIEngineGateway, 
    MessengerGateway, 
    MessagePresenter,
    ChatHistoryGateway,
    LoggerPort
)
from src.entities.chat import ChatMessage
from typing import List, Optional
import os

class ProcessMessageUseCase:
    def __init__(
        self, 
        ai_engine: AIEngineGateway, 
        messenger: MessengerGateway,
        presenter: MessagePresenter,
        logger: LoggerPort,
        allowed_users: List[int],
        history: Optional[ChatHistoryGateway] = None
    ):
        self.ai_engine = ai_engine
        self.messenger = messenger
        self.presenter = presenter
        self.logger = logger
        self.allowed_users = allowed_users
        self.history = history

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

        # 0. Persistir mensaje del usuario
        if self.history:
            message.role = "user"
            message.session_id = f"chat_{message.chat_id}"
            await self.history.save_message(message)

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
        
        # 3. Manejo de Adjuntos (Multimodal)
        attachments = []
        if message.photo_ids:
            self.logger.info(f"🖼️  Procesando {len(message.photo_ids)} fotos...")
            for photo_id in message.photo_ids:
                file_path = await self.messenger.get_file_path(photo_id)
                if file_path:
                    # Ruta local temporal
                    local_filename = f"photo_{photo_id}.jpg"
                    local_path = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "tmp", "downloads", local_filename)
                    
                    success = await self.messenger.download_file(file_path, local_path)
                    if success:
                        attachments.append(local_path)
                        self.logger.info(f"✅ Foto descargada: {local_path}")

        # LOG: Mensaje de entrada
        in_preview = message.text[:60] if len(message.text) > 60 else message.text
        self.logger.info(f"📥 [IN] {message.user_id}: \"{in_preview}\" {'📎 (+'+str(len(attachments))+' adjuntos)' if attachments else ''}")

        # 4. Consultar a la IA
        response = await self.ai_engine.ask(message.text, session_id=session_id, attachments=attachments)
        
        # 5. Limpieza de adjuntos temporales
        for path in attachments:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo eliminar archivo temporal {path}: {e}")
        
        # 6. Persistir y Validar respuesta de la IA
        # Si la respuesta está vacía tras la sanitización, la tratamos como error técnico
        if response.success and not response.text.strip():
            response.success = False
            response.error_message = "La IA devolvió una respuesta vacía o solo ruido técnico."
            self.logger.warning("⚠️ Respuesta de Gemini quedó vacía tras sanitización.")

        if response.success:
            out_preview = response.text[:60] if len(response.text) > 60 else response.text
            self.logger.info(f"📤 [OUT] Gemini: \"{out_preview}\"")
            
            if self.history:
                ai_msg = ChatMessage(
                    chat_id=message.chat_id,
                    user_id=0, # ID del bot
                    text=response.text,
                    role="assistant",
                    session_id=session_id
                )
                await self.history.save_message(ai_msg)
        else:
            self.logger.error(f"⚠️ [ERR] Gemini falló: {response.error_message}")
            # Sobreescribimos el texto para el presenter si falló
            response.text = "❌ <b>Lo siento</b>, estoy experimentando dificultades técnicas para procesar tu mensaje. Por favor, intenta de nuevo en unos momentos."

        # 7. Formatear respuesta vía Presenter (Capa de Presentación)
        formatted_messages = self.presenter.format_response(response)

        # 8. Enviar cada fragmento resultante
        for msg_text in formatted_messages:
            await self.messenger.send_message(
                chat_id=message.chat_id, 
                text=msg_text,
                parse_mode="HTML"
            )
