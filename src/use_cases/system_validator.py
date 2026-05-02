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
        messenger: MessengerGateway = None,
        webhook_url: str = "",
        secret_token: str = ""
    ):
        self.validators = validators
        self.messenger = messenger
        self.webhook_url = webhook_url
        self.secret_token = secret_token

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
        """Valida y sincroniza la salud del webhook en Telegram."""
        logger.info("Verificando salud del Webhook en Telegram...")
        try:
            status = await self.messenger.get_webhook_status()
            
            # Caso 1: No hay URL configurada o es distinta a la deseada
            if status.url != self.webhook_url:
                if not self.webhook_url:
                    logger.warning("No se ha configurado WEBHOOK_URL en el sistema local.")
                    return False
                
                logger.info(f"Sincronizando Webhook. URL actual: '{status.url}' -> Nueva: '{self.webhook_url}'")
                return await self.messenger.set_webhook(
                    url=self.webhook_url, 
                    secret_token=self.secret_token
                )
            
            logger.info(f"Webhook ya está correctamente sincronizado en: {status.url}")
            
            if status.last_error_message:
                logger.error(f"Telegram reporta errores en el webhook: {status.last_error_message}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"No se pudo verificar/sincronizar la salud de red: {e}")
            return False
