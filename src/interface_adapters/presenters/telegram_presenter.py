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
        Escapa caracteres especiales para Telegram MarkdownV2, preservando bloques de código.
        """
        # 1. Dividir por bloques de código (```...```) para no escapar su contenido de forma agresiva
        parts = re.split(r'(```[\s\S]*?```|`.*?`)', text)
        
        escaped_parts = []
        special_chars = r"_*[]()~`>#+-=|{}.!:"
        
        for i, part in enumerate(parts):
            # Si el índice es par, es texto normal (fuera de bloques de código)
            if i % 2 == 0:
                # Escapamos todos los caracteres especiales en texto plano
                escaped_part = re.sub(f"([{re.escape(special_chars)}])", r"\\\1", part)
                escaped_parts.append(escaped_part)
            else:
                # Es un bloque de código. Solo escapamos lo mínimo necesario para el bloque.
                # En MarkdownV2 dentro de ``` o `, solo se deben escapar \ y `
                # Pero en la práctica, Telegram es más permisivo dentro de bloques pre.
                # Sin embargo, si el bloque de código tiene backticks dentro, hay que tener cuidado.
                if part.startswith('```'):
                    # Bloque preformateado
                    # Escapamos solo contra-barras y backticks que cerrarían el bloque prematuramente
                    inner = part[3:-3]
                    # No escapamos el contenido interno de pre si usamos MarkdownV2 correctamente,
                    # PERO los delimitadores deben estar bien.
                    escaped_parts.append(f"```\n{inner.strip()}\n```")
                else:
                    # Código inline
                    inner = part[1:-1]
                    escaped_parts.append(f"`{inner}`")
                    
        return "".join(escaped_parts)

    def _chunk_text(self, text: str) -> List[str]:
        """Divide el texto en fragmentos que Telegram pueda procesar."""
        if len(text) <= self.max_length:
            return [text]
        
        chunks = []
        for i in range(0, len(text), self.max_length):
            chunks.append(text[i:i + self.max_length])
        return chunks
