"""
Path: src/use_cases/services/command_dispatcher.py
"""

from src.use_cases.ports.interfaces import AIEngineGateway, MessageGateway, LoggerPort
from src.entities.ai_session import AISession

class CommandDispatcher:
    """
    Gestiona la ejecución de comandos especiales de Telegram fuera del flujo de IA.
    """
    
    def __init__(self, ai_engine: AIEngineGateway, messenger: MessageGateway, logger: LoggerPort):
        self.ai_engine = ai_engine
        self.messenger = messenger
        self.logger = logger

    async def is_command(self, text: str) -> bool:
        """Determina si el texto es un comando soportado."""
        return text.strip().startswith("/")

    async def dispatch(self, command_text: str, chat_id: int, session: AISession) -> bool:
        """
        Procesa un comando y devuelve True si el flujo principal debe detenerse.
        """
        cmd = command_text.strip().lower()
        
        if cmd == "/reset":
            await self.messenger.set_typing(chat_id)
            success = await self.ai_engine.reset(session=session)
            msg = "🔄 <b>Contexto reiniciado</b>" if success else "❌ <b>Error al reiniciar</b>"
            await self.messenger.send_message(chat_id, msg, parse_mode="HTML")
            self.logger.info(f"♻️  Sesión reiniciada por el usuario en chat {chat_id}")
            return True
            
        if cmd == "/start":
            await self.messenger.send_message(
                chat_id, 
                "👋 <b>¡Hola!</b>\nSoy tu puente hacia Gemini con soporte para MCP.\n\nEscribime cualquier consulta o enviame fotos para analizar.",
                parse_mode="HTML"
            )
            return True

        return False
