"""
Path: src/interface_adapters/gateways/telegram_gateway.py
"""

from telegram import Bot
from src.use_cases.ports.interfaces import MessengerGateway, CredentialValidatorGateway
from src.entities.network import WebhookStatus
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramAdapter(MessengerGateway, CredentialValidatorGateway):
    def __init__(self, token: str):
        self.bot = Bot(token=token)

    async def validate(self) -> bool:
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Credenciales de Telegram validadas con éxito. Bot: @{bot_info.username}")
            return True
        except Exception as e:
            logger.error(f"Fallo en la validación de credenciales de Telegram: {e}")
            return False

    async def send_message(self, chat_id: int, text: str) -> bool:
        try:
            if len(text) > 4000:
                chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
                for chunk in chunks:
                    await self.bot.send_message(chat_id=chat_id, text=chunk)
            else:
                await self.bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            logger.error(f"Error enviando mensaje a Telegram: {e}")
            return False

    async def set_typing(self, chat_id: int) -> None:
        try:
            await self.bot.send_chat_action(chat_id=chat_id, action="typing")
        except Exception as e:
            logger.error(f"Error seteando typing: {e}")

    async def get_webhook_status(self) -> WebhookStatus:
        """Obtiene información del webhook desde Telegram."""
        try:
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
        except Exception as e:
            logger.error(f"Error consultando estado del webhook: {e}")
            raise e

    async def set_webhook(self, url: str, secret_token: Optional[str] = None) -> bool:
        """Registra la URL del webhook en los servidores de Telegram."""
        try:
            logger.info(f"Intentando registrar Webhook en: {url}")
            await self.bot.set_webhook(url=url, secret_token=secret_token)
            logger.info("Webhook registrado exitosamente en Telegram.")
            return True
        except Exception as e:
            logger.error(f"Error al registrar el Webhook: {e}")
            return False
