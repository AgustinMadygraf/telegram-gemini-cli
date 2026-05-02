"""
Path: src/use_cases/system_validator.py
"""

from src.use_cases.ports.interfaces import CredentialValidatorGateway, MessengerGateway
from typing import List
import logging

logger = logging.getLogger(__name__)

class SystemValidatorService:
    def __init__(
        self, 
        validators: List[CredentialValidatorGateway],
        messenger: MessengerGateway = None
    ):
        self.validators = validators
        self.messenger = messenger

    async def validate_all(self) -> bool:
        """Valida credenciales y opcionalmente la salud de la red."""
        logger.info("Iniciando validación de credenciales y sistema...")
        all_ok = True
        for validator in self.validators:
            if not await validator.validate():
                all_ok = False
        
        if self.messenger:
            if not await self.validate_network():
                all_ok = False
        
        if all_ok:
            logger.info("Sistema validado correctamente.")
        else:
            logger.error("Se encontraron fallos en la validación del sistema.")
            
        return all_ok

    async def validate_network(self) -> bool:
        """Valida la salud del webhook en Telegram."""
        logger.info("Verificando salud del Webhook en Telegram...")
        try:
            status = await self.messenger.get_webhook_status()
            if not status.url:
                logger.warning("El Webhook no tiene una URL configurada en Telegram.")
                return False
            
            logger.info(f"Webhook activo en: {status.url}")
            if status.last_error_message:
                logger.error(f"Último error de Telegram: {status.last_error_message} (Fecha: {status.last_error_date})")
                return False
            
            if status.pending_update_count > 10:
                logger.warning(f"Hay {status.pending_update_count} mensajes pendientes. Posible problema de latencia.")
            
            return True
        except Exception as e:
            logger.error(f"No se pudo verificar la salud de red: {e}")
            return False
