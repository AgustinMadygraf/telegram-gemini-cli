"""
Path: src/interface_adapters/presenters/telegram_presenter.py
"""

import re
import markdown
from typing import List
from src.entities.ai import AIResponse

class TelegramPresenter:
    def format_response(self, response: AIResponse) -> List[str]:
        """
        1. Convierte Markdown a HTML básico.
        2. Limpia etiquetas no soportadas por Telegram.
        3. Fragmenta si es necesario.
        """
        if not response.success:
            # Escapamos solo caracteres básicos de HTML para el error
            error_text = response.error_message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            error_msg = f"❌ <b>Error de IA</b>:\n<i>{error_text}</i>"
            return [error_msg]

        # 1. Convertir Markdown a HTML
        # Usamos extensiones básicas para manejar tablas y bloques de código
        raw_html = markdown.markdown(
            response.text, 
            extensions=['fenced_code', 'tables', 'nl2br']
        )

        # 2. Adaptar HTML para Telegram (Whitelist)
        telegram_html = self._sanitize_for_telegram(raw_html)
        
        # 3. Fragmentar por el límite de Telegram (4096 caracteres)
        return self._chunk_text(telegram_html)

    def _sanitize_for_telegram(self, html: str) -> str:
        """
        Filtra el HTML para que solo contenga etiquetas soportadas por Telegram:
        <b>, <i>, <u>, <s>, <code>, <pre>, <a>
        """
        # Reemplazar encabezados h1-h6 por negritas
        html = re.sub(r'<(h[1-6])>(.*?)</\1>', r'<b>\2</b>\n', html)
        
        # Reemplazar strong/em por b/i
        html = html.replace('<strong>', '<b>').replace('</strong>', '</b>')
        html = html.replace('<em>', '<i>').replace('</em>', '</i>')
        
        # Eliminar párrafos (reemplazar por saltos de línea)
        html = html.replace('<p>', '').replace('</p>', '\n')
        
        # Eliminar listas y otros elementos estructurales no soportados
        # (Conservamos el contenido pero quitamos las etiquetas ul, li, div, etc)
        html = re.sub(r'</?(ul|ol|li|div|span|br)>', '', html)
        
        # Limpieza final de espacios duplicados
        html = html.strip()
        
        return html

    def _chunk_text(self, text: str, limit: int = 4000) -> List[str]:
        """Fragmenta el texto respetando el límite de Telegram."""
        if len(text) <= limit:
            return [text]
            
        chunks = []
        while text:
            if len(text) <= limit:
                chunks.append(text)
                break
            
            # Buscamos el último salto de línea dentro del límite para no romper palabras
            split_pos = text.rfind('\n', 0, limit)
            if split_pos == -1:
                split_pos = limit
            
            chunks.append(text[:split_pos])
            text = text[split_pos:].strip()
            
        return chunks
