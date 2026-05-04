"""
Path: src/infrastructure/shell/local_filesystem.py
"""

import os
import shutil
from typing import List, Optional
from src.use_cases.ports.interfaces import FileSystemGateway

class LocalFileSystem(FileSystemGateway):
    def exists(self, path: str) -> bool:
        """Implementación real usando la librería estándar os."""
        return os.path.exists(path)

    def write_text(self, path: str, content: str) -> None:
        """Escribe contenido en un archivo."""
        with open(path, "w") as f:
            f.write(content)

    def read_text(self, path: str) -> str:
        """Lee el contenido de un archivo."""
        with open(path, "r") as f:
            return f.read()

    def delete(self, path: str) -> None:
        """Elimina un archivo."""
        if self.exists(path):
            os.remove(path)

    def ensure_dir(self, path: str) -> None:
        """Asegura que un directorio exista."""
        os.makedirs(path, exist_ok=True)

    def copy_directory(self, src: str, dst: str, ignore_patterns: List[str] = None) -> None:
        """Copia un directorio usando shutil.copytree."""
        ignore = shutil.ignore_patterns(*ignore_patterns) if ignore_patterns else None
        shutil.copytree(src, dst, ignore=ignore)

    def remove_directory(self, path: str) -> None:
        """Elimina un directorio usando shutil.rmtree."""
        if self.exists(path):
            shutil.rmtree(path)

    def get_absolute_path(self, path: str) -> str:
        """Obtiene la ruta absoluta."""
        return os.path.abspath(path)
