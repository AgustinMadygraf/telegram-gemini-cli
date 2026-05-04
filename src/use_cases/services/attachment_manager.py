"""
Path: src/use_cases/services/attachment_manager.py
"""

import os
from typing import List, Optional
from src.use_cases.ports.interfaces import FileGateway, LoggerPort

class AttachmentManager:
    """
    Gestiona el ciclo de vida de los archivos adjuntos (fotos, documentos) 
    durante el procesamiento de un mensaje.
    """
    
    def __init__(self, file_gateway: FileGateway, logger: LoggerPort, download_path: str):
        self.file_gateway = file_gateway
        self.logger = logger
        self.download_path = download_path

    async def download_attachments(self, photo_ids: List[str]) -> List[str]:
        """Descarga una lista de fotos y devuelve sus rutas locales."""
        local_paths = []
        if not self.file_gateway:
            return local_paths

        for photo_id in photo_ids:
            try:
                file_remote_path = await self.file_gateway.get_file_path(photo_id)
                if not file_remote_path:
                    continue

                local_filename = f"photo_{photo_id}.jpg"
                local_full_path = os.path.join(self.download_path, local_filename)
                
                success = await self.file_gateway.download_file(file_remote_path, local_full_path)
                if success:
                    local_paths.append(local_full_path)
                    self.logger.debug(f"📥 Archivo descargado: {local_full_path}")
            except Exception as e:
                self.logger.error(f"❌ Error descargando adjunto {photo_id}: {e}")
        
        return local_paths

    def cleanup(self, local_paths: List[str]) -> None:
        """Elimina los archivos temporales de forma segura."""
        for path in local_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    self.logger.debug(f"🧹 Archivo temporal eliminado: {path}")
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo eliminar archivo temporal {path}: {e}")
