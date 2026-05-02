"""
Path: src/interface_adapters/presenters/telegram_presenter.py
"""

import re
from typing import List
from src.use_cases.ports.interfaces import MessagePresenter
from src.entities.ai import AIResponse

class TelegramPresenter(MessagePresenter):
    def __init__(self, max_length: int = 4090):
        self.max_length = max_length

    def format_response(self, response: AIResponse) -> List[str]:
        """
        Formatea la respuesta para Telegram MarkdownV2.
        1. Maneja errores.
        2. Escapa caracteres especiales.
        3. Fragmenta si es necesario.
        """
        if not response.success:
            error_msg = f"❌ *Error de IA*:\n_{self._escape(response.error_message)}_"
            return [error_msg]

        text = response.text
        # Aquí podríamos procesar el texto (ej: convertir negritas de Markdown a MarkdownV2)
        # Por ahora, nos aseguramos de que sea seguro para Telegram.
        
        escaped_text = self._escape(text)
        return self._chunk_text(escaped_text)

    def _escape(self, text: str) -> str:
        """
        Escapa caracteres especiales para Telegram MarkdownV2.
        Referencia: https://core.telegram.org/bots/api#markdownv2-style
        """
        # Caracteres que DEBEN ser escapados
        special_chars = r"_*[]()~`>#+-=|{}.!"
        return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", text)

    def _chunk_text(self, text: str) -> List[str]:
        """Divide el texto en fragmentos que Telegram pueda procesar."""
        if len(text) <= self.max_length:
            return [text]
        
        chunks = []
        for i in range(0, len(text), self.max_length):
            chunks.append(text[i:i + self.max_length])
        return chunks
