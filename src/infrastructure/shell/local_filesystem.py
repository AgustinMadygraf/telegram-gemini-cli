"""
Path: src/infrastructure/shell/local_filesystem.py
"""

import os
from src.use_cases.ports.interfaces import FileSystemGateway

class LocalFileSystem(FileSystemGateway):
    def exists(self, path: str) -> bool:
        """Implementación real usando la librería estándar os."""
        return os.path.exists(path)

    def write_file(self, path: str, content: str) -> None:
        """Escribe contenido en un archivo (puro síncrono)."""
        with open(path, "w") as f:
            f.write(content)

    def ensure_dir(self, path: str) -> None:
        """Asegura que un directorio exista."""
        os.makedirs(path, exist_ok=True)
