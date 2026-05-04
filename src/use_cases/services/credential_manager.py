"""
Path: src/use_cases/services/credential_manager.py
"""

from src.use_cases.ports.interfaces import FileSystemGateway, LoggerPort
import os

class CredentialSyncService:
    """
    Servicio encargado de gestionar la persistencia y sincronización de identidad (OAuth)
    entre el entorno global y los entornos aislados de las sesiones.
    """
    
    def __init__(self, fs: FileSystemGateway, logger: LoggerPort):
        self.fs = fs
        self.logger = logger

    def sync_credentials(self, target_path: str) -> None:
        """
        Sincroniza las credenciales de Google Auth desde el directorio global 
        hacia un path de destino específico.
        """
        global_config_dir = os.path.expanduser("~/.gemini")
        target_config_dir = os.path.join(target_path, ".gemini")

        if not self.fs.exists(global_config_dir):
            self.logger.warning(f"⚠️ No se encontró directorio global de credenciales en {global_config_dir}")
            return

        # Sincronización selectiva: verificamos que el archivo esencial exista.
        # El directorio .gemini puede ser creado por Gemini CLI sin los archivos de auth.
        target_settings = os.path.join(target_config_dir, "settings.json")
        if not self.fs.exists(target_settings):
            try:
                self.logger.info(f"🔑 Sincronizando identidad OAuth hacia {target_config_dir}")
                self.fs.copy_directory(
                    global_config_dir, 
                    target_config_dir, 
                    ignore_patterns=["tmp*", "sessions*", "logs*", "antigravity*", "history*"]
                )
            except Exception as e:
                self.logger.error(f"❌ Error crítico copiando credenciales: {e}")
                raise
        
        # Siempre sanear para asegurar integridad en cada mensaje
        self._sanitize_session_settings(target_config_dir)

    def _sanitize_session_settings(self, config_dir: str) -> None:
        """
        Sanea el settings.json de la sesión eliminando únicamente los servidores MCP
        cuyos scripts no existen en disco (para evitar crashes del CLI).
        La sección mcpServers debe persistir porque es lo que le dice a Gemini CLI
        qué servidores conectar. --include-directories solo expone rutas al workspace.
        """
        import json
        settings_path = os.path.join(config_dir, "settings.json")
        if not self.fs.exists(settings_path):
            return

        try:
            content = self.fs.read_text(settings_path)
            data = json.loads(content)
            
            mcp_servers = data.get("mcpServers", {})
            if not mcp_servers:
                return
            
            # Solo eliminamos servidores cuyo script no existe en disco
            invalid_servers = []
            for name, details in mcp_servers.items():
                args = details.get("args", [])
                if args and not os.path.exists(args[0]):
                    invalid_servers.append(name)
                    self.logger.warning(f"⚠️ MCP '{name}': Script no encontrado ({args[0]}), removido de la sesión")
            
            if invalid_servers:
                for name in invalid_servers:
                    del mcp_servers[name]
                self.fs.write_text(settings_path, json.dumps(data, indent=2))
                    
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo limpiar settings.json de la sesión: {e}")

