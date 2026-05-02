"""
Path: src/infrastructure/markdown/markdown_adapter.py
"""

import markdown
from src.use_cases.ports.interfaces import MarkdownConverterPort

class PythonMarkdownAdapter(MarkdownConverterPort):
    def to_html(self, text: str) -> str:
        """Convierte Markdown a HTML usando la librería 'markdown' de Python."""
        return markdown.markdown(
            text, 
            extensions=['fenced_code', 'tables', 'nl2br']
        )
