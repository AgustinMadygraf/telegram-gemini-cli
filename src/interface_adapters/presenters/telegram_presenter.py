"""
Path: src/interface_adapters/presenters/telegram_presenter.py
"""

import re
import logging
from typing import List
from src.entities.ai import AIResponse
from src.use_cases.ports.interfaces import MarkdownConverterPort

logger = logging.getLogger(__name__)

class TelegramPresenter:
    def __init__(self, markdown_converter: MarkdownConverterPort):
        self.markdown_converter = markdown_converter

    def format_response(self, response: AIResponse) -> List[str]:
        """
        1. Convierte Markdown a HTML básico.
        2. Limpia etiquetas no soportadas.
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
            logger.error(f"Error en conversión Markdown: {str(e)}")
            # Fallback a texto plano escapado
            return self._chunk_text(response.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

        # 2. Adaptar HTML para Telegram (Robust Sanitization)
        telegram_html = self._sanitize_for_telegram(raw_html)
        
        # 3. Fragmentar por el límite de Telegram
        return self._chunk_text(telegram_html)

    def _sanitize_for_telegram(self, html: str) -> str:
        """
        Refina el HTML para que sea 100% compatible con Telegram.
        """
        # A. Manejo de Bloques de Código
        # Telegram prefiere <pre><code>...</code></pre> sin clases de lenguaje adicionales
        html = re.sub(r'<pre><code class=".*?">', '<pre><code>', html)
        
        # B. Conversión de Encabezados a Negritas
        html = re.sub(r'<(h[1-6])>(.*?)</\1>', r'<b>\2</b>\n', html)
        
        # C. Conversión de Listas (Markdown produce <ul><li>...</li></ul>)
        # Reemplazamos <li> por un bullet point
        html = html.replace('<li>', '• ').replace('</li>', '\n')
        
        # D. Mapeo de estilos estándar
        html = html.replace('<strong>', '<b>').replace('</strong>', '</b>')
        html = html.replace('<em>', '<i>').replace('</em>', '</i>')
        
        # E. Eliminación de etiquetas estructurales no permitidas (Whitelist Negativa)
        # Quitamos <ul>, <ol>, <p>, <div>, <span>, <table>, <tr>, <td>, etc.
        # Pero conservamos su contenido.
        unsupported = ['ul', 'ol', 'p', 'div', 'span', 'table', 'tbody', 'tr', 'td', 'thead', 'hr']
        for tag in unsupported:
            html = re.sub(f'</?{tag}.*?>', '', html)
        
        # F. Limpieza de saltos de línea excesivos (máximo 2 juntos)
        html = re.sub(r'\n{3,}', '\n\n', html)
        
        return html.strip()

    def _chunk_text(self, text: str, limit: int = 4000) -> List[str]:
        """Fragmenta el texto respetando el límite de Telegram y etiquetas."""
        if len(text) <= limit:
            return [text]
            
        chunks = []
        while text:
            if len(text) <= limit:
                chunks.append(text)
                break
            
            # Buscar el último salto de línea dentro del límite
            split_pos = text.rfind('\n', 0, limit)
            if split_pos == -1:
                split_pos = limit
            
            chunks.append(text[:split_pos])
            text = text[split_pos:].strip()
            
        return chunks
