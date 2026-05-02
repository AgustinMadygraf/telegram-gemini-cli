"""
Path: src/interface_adapters/gateways/telegram_gateway.py
"""

from telegram import Bot
from src.use_cases.ports.interfaces import MessengerGateway, CredentialValidatorGateway
import logging

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
