"""
Path: src/infrastructure/shell/local_filesystem.py
"""

import os
from src.use_cases.ports.interfaces import FileSystemGateway

class LocalFileSystem(FileSystemGateway):
    def exists(self, path: str) -> bool:
        """Implementación real usando la librería estándar os."""
        return os.path.exists(path)
