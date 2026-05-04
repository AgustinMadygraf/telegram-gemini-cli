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
        Elimina la sección mcpServers del settings.json de la sesión.
        Esto obliga a Gemini CLI a usar únicamente los servidores que nosotros
        le pasamos por línea de comandos (ya validados).
        """
        import json
        settings_path = os.path.join(config_dir, "settings.json")
        if not self.fs.exists(settings_path):
            return

        try:
            content = self.fs.read_text(settings_path)
            data = json.loads(content)
            
            if "mcpServers" in data:
                del data["mcpServers"]
                self.fs.write_text(settings_path, json.dumps(data, indent=2))
                self.logger.info("🧹 Configuración de MCPs globales eliminada de la sesión (se usará inyección por CLI)")
                    
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo limpiar settings.json de la sesión: {e}")
