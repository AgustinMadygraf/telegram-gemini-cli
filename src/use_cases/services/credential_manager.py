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

        # Sincronización selectiva (Copy only if missing)
        if not self.fs.exists(target_config_dir):
            try:
                self.logger.info(f"🔑 Sincronizando identidad OAuth hacia {target_config_dir}")
                self.fs.copy_directory(
                    global_config_dir, 
                    target_config_dir, 
                    ignore_patterns=["tmp*", "sessions*", "logs*", "antigravity*"]
                )
            except Exception as e:
                self.logger.error(f"❌ Error crítico copiando credenciales: {e}")
                raise
        
        # Siempre sanear para asegurar integridad en cada mensaje
        self._sanitize_session_settings(target_config_dir)

    def _sanitize_session_settings(self, config_dir: str) -> None:
        """
        Limpia el settings.json de la sesión eliminando MCPs con paths inexistentes.
        """
        import json
        settings_path = os.path.join(config_dir, "settings.json")
        if not self.fs.exists(settings_path):
            return

        try:
            content = self.fs.read_text(settings_path)
            data = json.loads(content)
            
            if "mcpServers" in data:
                original_count = len(data["mcpServers"])
                valid_mcp = {}
                
                for name, config in data["mcpServers"].items():
                    args = config.get("args", [])
                    if args and os.path.isabs(args[0]):
                        if os.path.exists(args[0]): # Usamos os.path directo para velocidad
                            valid_mcp[name] = config
                        else:
                            self.logger.debug(f"🧹 Eliminando MCP inválido de la sesión: {name}")
                
                data["mcpServers"] = valid_mcp
                
                if len(valid_mcp) != original_count:
                    self.fs.write_text(settings_path, json.dumps(data, indent=2))
                    self.logger.info(f"✅ settings.json saneado ({len(valid_mcp)}/{original_count} MCPs válidos)")
                    
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo sanear settings.json de la sesión: {e}")
