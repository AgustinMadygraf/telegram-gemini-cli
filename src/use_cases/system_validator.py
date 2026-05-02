"""
Path: src/use_cases/system_validator.py
"""

from src.use_cases.ports.interfaces import CredentialValidatorGateway, MessengerGateway, TunnelGateway
from src.entities.validation import ValidationReport
from typing import List

class SystemValidatorService:
    def __init__(
        self, 
        validators: List[CredentialValidatorGateway],
        messenger: MessengerGateway = None,
        tunnel: TunnelGateway = None,
        webhook_url: str = "",
        secret_token: str = ""
    ):
        self.validators = validators
        self.messenger = messenger
        self.tunnel = tunnel
        self.webhook_url = webhook_url
        self.secret_token = secret_token

    async def validate_all(self) -> ValidationReport:
        """Valida credenciales, red y túneles devolviendo un reporte detallado."""
        report = ValidationReport()
        report.add_info("Iniciando validación de sistema (Deep Health Check)...")
        
        # 1. Validar Credenciales (Gemini, Telegram)
        for validator in self.validators:
            if not await validator.validate():
                report.add_error(f"Fallo en validador de credenciales: {validator.__class__.__name__}")
        
        # 2. Validar Túnel (Cloudflare)
        if self.tunnel:
            report.add_info(f"Validando estado del túnel para: {self.webhook_url}")
            if not await self.tunnel.validate_tunnel():
                report.add_error("El túnel de comunicación no está saludable o el token no ha sido configurado.")
        else:
            report.add_info("No se ha configurado un gestor de túneles. Se omite validación profunda.")

        # 3. Validar y Sincronizar Red (Webhook)
        if self.messenger:
            await self._validate_network(report)
        
        if report.is_ok:
            report.add_info("Sistema validado correctamente.")
        else:
            report.add_critical("Se encontraron fallos en la validación del sistema.")
            
        return report

    async def _validate_network(self, report: ValidationReport):
        """Valida y sincroniza la salud del webhook en Telegram."""
        report.add_info("Verificando salud del Webhook en Telegram...")
        try:
            status = await self.messenger.get_webhook_status()
            
            # Caso 1: No hay URL configurada o es distinta a la deseada
            if status.url != self.webhook_url:
                if not self.webhook_url:
                    report.add_error("No se ha configurado WEBHOOK_URL en el sistema local.")
                    return
                
                report.add_info(f"Sincronizando Webhook. URL actual: '{status.url}' -> Nueva: '{self.webhook_url}'")
                success = await self.messenger.set_webhook(
                    url=self.webhook_url, 
                    secret_token=self.secret_token
                )
                if not success:
                    report.add_error("Fallo al intentar registrar el nuevo Webhook.")
            else:
                report.add_info(f"Webhook ya está correctamente sincronizado en: {status.url}")
            
            if status.last_error_message:
                report.add_error(f"Telegram reporta errores en el webhook: {status.last_error_message}")
                
        except Exception as e:
            report.add_error(f"No se pudo verificar/sincronizar la salud de red: {e}")
