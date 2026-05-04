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

        # Si ya existe en el destino, saltamos (Lazy Sync)
        if self.fs.exists(target_config_dir):
            self.logger.debug(f"ℹ️ Credenciales ya presentes en {target_config_dir}. Saltando.")
            return

        try:
            self.logger.info(f"🔑 Sincronizando identidad OAuth hacia {target_config_dir}")
            self.fs.copy_directory(
                global_config_dir, 
                target_config_dir, 
                ignore_patterns=["tmp*", "sessions*", "logs*", "antigravity*"]
            )
        except Exception as e:
            self.logger.error(f"❌ Error crítico sincronizando credenciales: {e}")
            raise
