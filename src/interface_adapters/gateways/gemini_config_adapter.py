"""
Path: src/interface_adapters/gateways/gemini_config_adapter.py
"""

import os
import json
from typing import List
from src.use_cases.ports.interfaces import GeminiConfigGateway, FileSystemGateway, LoggerPort

class GeminiLocalConfigAdapter(GeminiConfigGateway):
    """
    Adaptador que lee la configuración local de Gemini CLI (~/.gemini/settings.json)
    para proveer metadatos al sistema.
    """
    
    def __init__(self, fs: FileSystemGateway, logger: LoggerPort, config_path: str = None):
        self.fs = fs
        self.logger = logger
        self.config_path = config_path or os.path.expanduser("~/.gemini/settings.json")

    def get_include_directories(self) -> List[str]:
        """
        Extrae los paths de los servidores MCP para incluirlos en el sandbox.
        """
        if not self.fs.exists(self.config_path):
            self.logger.debug(f"ℹ️ No se encontró settings.json en {self.config_path}")
            return []

        try:
            content = self.fs.read_text(self.config_path)
            config = json.loads(content)
            mcp_servers = config.get("mcpServers", {})
            
            paths = set()
            for name, details in mcp_servers.items():
                args = details.get("args", [])
                if args:
                    script_path = args[0]
                    if os.path.isabs(script_path):
                        paths.add(os.path.dirname(script_path))
            
            return list(paths)
        except Exception as e:
            self.logger.warning(f"⚠️ Error al leer configuración de Gemini: {e}")
            return []
