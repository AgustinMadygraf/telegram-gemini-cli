"""
Path: src/interface_adapters/gateways/mcp_validator_adapter.py
"""

import json
import os
from typing import List, Tuple
from src.use_cases.ports.interfaces import MCPValidatorGateway, FileSystemGateway, AIEngineGateway

class MCPValidatorAdapter(MCPValidatorGateway):
    def __init__(self, fs: FileSystemGateway, ai_engine: AIEngineGateway, config_path: str = None):
        self.fs = fs
        self.ai_engine = ai_engine
        self.config_path = config_path or os.path.expanduser("~/.gemini/settings.json")

    async def validate_servers(self) -> List[Tuple[str, bool, str]]:
        """
        Valida los servidores MCP leyendo el settings.json de Gemini.
        """
        if not self.fs.exists(self.config_path):
            return [("Configuración", False, f"No se encontró el archivo de configuración en {self.config_path}")]

        try:
            # Nota: Usamos open directo aquí ya que FileSystemGateway suele ser para el sandbox,
            # pero para leer el settings global usamos el sistema.
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            return [("Configuración", False, f"Error al parsear JSON: {str(e)}")]

        # 1. Validación estática (existencia de archivos)
        mcp_servers = config.get("mcpServers", {})
        if not mcp_servers:
            return [("Ecosistema MCP", True, "No hay servidores MCP configurados.")]

        # 2. Validación de comportamiento (Deep Check vía IA)
        ai_mcp_info = await self.ai_engine.get_mcp_info()
        
        results = []
        for name, details in mcp_servers.items():
            command = details.get("command")
            args = details.get("args", [])
            
            # Chequeo físico
            file_exists = True
            error_msg = ""
            
            if command in ["node", "npx", "python", "python3", "uvx"] and args:
                script_path = args[0]
                if not self.fs.exists(script_path):
                    file_exists = False
                    error_msg = f"Script no encontrado en: {script_path}."
            
            # Chequeo de visibilidad para la IA
            # Si el nombre del servidor aparece en la salida de la IA como desconectado
            # (El formato de gemini mcp list suele indicar el estado)
            is_connected = True
            if file_exists:
                # Buscamos si el servidor aparece como 'disconnected' o similar en la salida
                # Nota: Ajustamos la lógica según el formato observado: "aparecen como desconectados"
                if name.lower() in ai_mcp_info.lower() and ("disconnected" in ai_mcp_info.lower() or "desconectado" in ai_mcp_info.lower()):
                    is_connected = False
                    error_msg = "⚠️  Archivo presente pero DESCONECTADO (posible bloqueo de Sandbox)."
            
            final_status = file_exists and is_connected
            results.append((name, final_status, error_msg))

        return results
