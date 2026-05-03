"""
Path: src/interface_adapters/gateways/mcp_validator_adapter.py
"""

import json
import os
from typing import List, Tuple
from src.use_cases.ports.interfaces import MCPValidatorGateway, FileSystemGateway

class MCPValidatorAdapter(MCPValidatorGateway):
    def __init__(self, fs: FileSystemGateway, config_path: str = None):
        self.fs = fs
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

        mcp_servers = config.get("mcpServers", {})
        if not mcp_servers:
            return [("Ecosistema MCP", True, "No hay servidores MCP configurados.")]

        results = []
        for name, details in mcp_servers.items():
            command = details.get("command")
            args = details.get("args", [])
            
            # Verificación básica para servidores STDIO (Node/Python)
            if command in ["node", "npx", "python", "python3", "uvx"] and args:
                script_path = args[0]
                # Verificamos si el path existe
                if self.fs.exists(script_path):
                    results.append((name, True, ""))
                else:
                    # Sugerencia de reparación
                    suggestion = f"Script no encontrado en: {script_path}. Asegúrate de haber clonado el repo y ejecutado el build."
                    results.append((name, False, suggestion))
            
            # Verificación para servidores SSE (Basado en convención futura)
            elif "url" in details:
                # Por ahora reportamos como advertencia de que falta el ping
                results.append((name, True, "(SSE detectado - Conectividad asumida)"))
            
            else:
                results.append((name, False, "Tipo de transporte MCP no soportado o argumentos faltantes."))

        return results
