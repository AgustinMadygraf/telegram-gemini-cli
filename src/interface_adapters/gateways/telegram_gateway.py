"""
Path: src/interface_adapters/gateways/telegram_gateway.py
"""

from telegram import Bot
from telegram.error import TelegramError
from src.use_cases.ports.interfaces import MessengerGateway, CredentialValidatorGateway, LoggerPort
from src.entities.network import WebhookStatus
from typing import Optional

class TelegramAdapter(MessengerGateway, CredentialValidatorGateway):
    def __init__(self, token: str, logger: LoggerPort):
        self.bot = Bot(token=token)
        self.logger = logger

    async def validate(self) -> bool:
        """Valida las credenciales del bot."""
        try:
            await self.bot.get_me()
            return True
        except Exception as e:
            self.logger.error(f"Error validando bot: {str(e)}")
            return False

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Envía mensajes con alta observabilidad delegada al puerto de logging."""
        try:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=text, 
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            self.logger.error(f"❌ Error de Telegram ({e.message}) al enviar mensaje a {chat_id}")
            self.logger.error(f"📄 Payload fallido (Modo: {parse_mode}):\n--- START ---\n{text}\n--- END ---")
            return False
        except Exception as e:
            self.logger.error(f"💥 Error inesperado en el adaptador: {str(e)}")
            return False

    async def set_typing(self, chat_id: int) -> None:
        """Notifica que el bot está escribiendo."""
        try:
            await self.bot.send_chat_action(chat_id=chat_id, action="typing")
        except Exception:
            pass

    async def get_webhook_status(self) -> WebhookStatus:
        """Obtiene información técnica del webhook."""
        info = await self.bot.get_webhook_info()
        return WebhookStatus(
            url=info.url,
            has_custom_certificate=info.has_custom_certificate,
            pending_update_count=info.pending_update_count,
            last_error_date=info.last_error_date,
            last_error_message=info.last_error_message,
            max_connections=info.max_connections,
            ip_address=info.ip_address
        )

    async def set_webhook(self, url: str, secret_token: Optional[str] = None) -> bool:
        """Registra la URL del webhook."""
        try:
            return await self.bot.set_webhook(url=url, secret_token=secret_token)
        except TelegramError as e:
            self.logger.error(f"Error configurando Webhook: {e.message}")
            raise e
        except Exception as e:
            self.logger.error(f"Error inesperado configurando Webhook: {str(e)}")
            return False
