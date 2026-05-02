"""
Path: src/interface_adapters/presenters/telegram_presenter.py
"""

import re
from typing import List
from src.entities.ai import AIResponse
from src.use_cases.ports.interfaces import MarkdownConverterPort, LoggerPort

class TelegramPresenter:
    def __init__(self, markdown_converter: MarkdownConverterPort, logger: LoggerPort):
        self.markdown_converter = markdown_converter
        self.logger = logger

    def format_response(self, response: AIResponse) -> List[str]:
        """
        1. Convierte Markdown a HTML básico delegando en el puerto.
        2. Limpia etiquetas no soportadas por Telegram.
        3. Fragmenta si es necesario.
        """
        if not response.success:
            error_text = response.error_message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            error_msg = f"❌ <b>Error de IA</b>:\n<i>{error_text}</i>"
            return [error_msg]

        # 1. Convertir Markdown a HTML
        try:
            raw_html = self.markdown_converter.to_html(response.text)
        except Exception as e:
            self.logger.error(f"Error en conversión Markdown: {str(e)}")
            return self._chunk_text(response.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

        # 2. Adaptar HTML para Telegram
        telegram_html = self._sanitize_for_telegram(raw_html)
        
        # 3. Fragmentar por el límite de Telegram
        return self._chunk_text(telegram_html)

    def _sanitize_for_telegram(self, html: str) -> str:
        """Filtra el HTML para que sea 100% compatible con Telegram."""
        html = re.sub(r'<pre><code class=".*?">', '<pre><code>', html)
        html = re.sub(r'<(h[1-6])>(.*?)</\1>', r'<b>\2</b>\n', html)
        html = html.replace('<li>', '• ').replace('</li>', '\n')
        html = html.replace('<strong>', '<b>').replace('</strong>', '</b>')
        html = html.replace('<em>', '<i>').replace('</em>', '</i>')
        
        # E. Eliminación de etiquetas estructurales no permitidas (Whitelist Negativa)
        # Reemplazamos <br> por salto de línea antes de eliminar el resto
        html = re.sub(r'<br\s*/?>', '\n', html)
        
        unsupported = ['ul', 'ol', 'p', 'div', 'span', 'table', 'tbody', 'tr', 'td', 'thead', 'hr']
        for tag in unsupported:
            html = re.sub(f'</?{tag}.*?>', '', html)
        
        html = re.sub(r'\n{3,}', '\n\n', html)
        return html.strip()

    def _chunk_text(self, text: str, limit: int = 4000) -> List[str]:
        """Fragmenta el texto respetando el límite de Telegram."""
        if len(text) <= limit:
            return [text]
            
        chunks = []
        while text:
            if len(text) <= limit:
                chunks.append(text)
                break
            
            split_pos = text.rfind('\n', 0, limit)
            if split_pos == -1:
                split_pos = limit
            
            chunks.append(text[:split_pos])
            text = text[split_pos:].strip()
            
        return chunks
