"""
Path: src/use_cases/system_validator.py
"""

from src.use_cases.ports.interfaces import CredentialValidatorGateway
from typing import List
import logging

logger = logging.getLogger(__name__)

class SystemValidatorService:
    def __init__(self, validators: List[CredentialValidatorGateway]):
        self.validators = validators

    async def validate_all(self) -> bool:
        logger.info("Iniciando validación de credenciales y sistema...")
        all_ok = True
        for validator in self.validators:
            if not await validator.validate():
                all_ok = False
        
        if all_ok:
            logger.info("Sistema validado correctamente.")
        else:
            logger.error("Se encontraron fallos en la validación del sistema.")
            
        return all_ok
