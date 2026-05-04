"""
Path: src/interface_adapters/gateways/gemini_config_adapter.py
"""

import os
import json
from typing import List
from src.use_cases.ports.interfaces import GeminiConfigGateway, FileGateway, LoggerPort, AIEngineGateway

class GeminiLocalConfigAdapter(GeminiConfigGateway):
    """
    Lee la configuración local de Gemini para extraer información útil 
    para la ejecución aislada (sandbox).
    """
    
    def __init__(self, fs: FileGateway, logger: LoggerPort):
        self.fs = fs
        self.logger = logger

    def get_include_directories(self) -> List[str]:
        """
        Extrae los directorios de los servidores MCP configurados para incluirlos en el sandbox.
        """
        settings_path = os.path.expanduser("~/.gemini/settings.json")
        if not self.fs.exists(settings_path):
            return []

        try:
            content = self.fs.read_text(settings_path)
            data = json.loads(content)
            mcp_servers = data.get("mcpServers", {})
            
            paths = set()
            for name, details in mcp_servers.items():
                args = details.get("args", [])
                if args:
                    script_path = args[0]
                    if os.path.isabs(script_path):
                        dir_path = os.path.dirname(script_path)
                        # Verificación física rigurosa
                        if os.path.isdir(dir_path):
                            paths.add(dir_path)
                        else:
                            self.logger.debug(f"ℹ️ Saltando directorio MCP inexistente: {dir_path}")
            
            return list(paths)
        except Exception as e:
            self.logger.error(f"⚠️ Error leyendo configuración de MCPs: {e}")
            return []

class BaseMCPValidatorAdapter:
    def __init__(self, fs: FileGateway, ai_engine: AIEngineGateway):
        self.fs = fs
        self.ai_engine = ai_engine
        from src.infrastructure.logging.standard_logger import StandardLoggerAdapter
        self.logger = StandardLoggerAdapter("system.mcp_validator")
    async def validate(self) -> bool:
        """
        Valida el ecosistema MCP verificando configuración y existencia física.
        """
        try:
            raw_info = await self.ai_engine.get_mcp_info()
            
            import re
            mcp_names = re.findall(r"-\s*(\w+)", raw_info)
            
            if not mcp_names:
                self.logger.warning("⚠️ No se encontraron servidores MCP configurados.")
                return True

            settings_path = os.path.expanduser("~/.gemini/settings.json")
            mcp_config = {}
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    data = json.load(f)
                    mcp_config = data.get("mcpServers", {})

            for name in mcp_names:
                config = mcp_config.get(name, {})
                args = config.get("args", [])
                
                path_exists = False
                if args and os.path.exists(args[0]):
                    path_exists = True
                
                if path_exists:
                    self.logger.info(f"✅ MCP '{name}': Conectado/Disponible")
                else:
                    self.logger.warning(f"❌ MCP '{name}': Error (Script no encontrado en disco)")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Error validando ecosistema MCP: {e}")
            return False

class MCPValidatorAdapter(BaseMCPValidatorAdapter):
    """
    Validador de salud del ecosistema MCP.
    """
    pass

