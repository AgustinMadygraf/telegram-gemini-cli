"""
Path: src/use_cases/system_validator.py
"""

from src.use_cases.ports.interfaces import (
    CredentialValidatorGateway, 
    MessengerGateway, 
    TunnelGateway, 
    MCPValidatorGateway,
    LoggerPort
)
from src.entities.validation import ValidationReport
from typing import List

class SystemValidatorService:
    def __init__(
        self, 
        validators: List[CredentialValidatorGateway],
        logger: LoggerPort,
        messenger: MessengerGateway = None,
        tunnel: TunnelGateway = None,
        mcp_validator: MCPValidatorGateway = None,
        webhook_url: str = "",
        secret_token: str = ""
    ):
        self.validators = validators
        self.logger = logger
        self.messenger = messenger
        self.tunnel = tunnel
        self.mcp_validator = mcp_validator
        self.webhook_url = webhook_url
        self.secret_token = secret_token

    async def validate_all(self) -> ValidationReport:
        """Valida credenciales, red y túneles devolviendo un reporte detallado."""
        report = ValidationReport()
        self._report_info(report, "Iniciando validación de sistema (Deep Health Check)")

        # 0. Reportar Estrategia de IA
        from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
        for v in self.validators:
            if isinstance(v, GeminiCLIAdapter):
                self._report_info(report, f"Estrategia de IA: {v.auth_method.upper()}")
        
        # 1. Validar Credenciales (Gemini, Telegram)
        for validator in self.validators:
            if not await validator.validate():
                self._report_error(report, f"Fallo en validador de credenciales: {validator.__class__.__name__}")
        
        # 2. Validar Túnel (Cloudflare)
        if self.tunnel:
            self._report_info(report, f"Validando estado del túnel para: {self.webhook_url}")
            if not await self.tunnel.validate_tunnel(url=self.webhook_url):
                # FLEXIBILIDAD: Solo es un error crítico si estamos en producción (podría ser un flag)
                # Por ahora, lo bajamos a advertencia para permitir el desarrollo.
                self._report_info(report, "⚠️  Túnel no detectado o token faltante. Se permite continuar en modo degradado.")
        else:
            self._report_info(report, "No se ha configurado un gestor de túneles.")

        # 3. Validar y Sincronizar Red (Webhook)
        if self.messenger:
            await self._validate_network(report)
        
        # 4. Validar Ecosistema MCP
        if self.mcp_validator:
            await self._validate_mcp(report)
        
        if report.is_ok:
            self._report_info(report, "Sistema validado correctamente.")
        else:
            self._report_critical(report, "Se encontraron fallos críticos que impiden el arranque seguro.")
            
        return report

    def _report_info(self, report, msg):
        report.add_info(msg)
        self.logger.info(f"✅ {msg}")

    def _report_error(self, report, msg):
        report.add_error(msg)
        self.logger.error(f"❌ {msg}")

    def _report_critical(self, report, msg):
        report.add_critical(msg)
        self.logger.critical(f"🔥 {msg}")

    async def _validate_network(self, report: ValidationReport):
        """Valida y sincroniza la salud del webhook en Telegram."""
        self._report_info(report, "Verificando salud del Webhook en Telegram")
        try:
            status = await self.messenger.get_webhook_status()
            
            if status.url != self.webhook_url or status.last_error_message:
                self._report_info(report, f"Sincronizando Webhook (Limpieza de estado): '{self.webhook_url}'")
                try:
                    await self.messenger.set_webhook(
                        url=self.webhook_url, 
                        secret_token=self.secret_token
                    )
                    self._report_info(report, "Webhook sincronizado con éxito.")
                    # Si acabamos de sincronizar con éxito, ignoramos el error anterior que venía en 'status'
                    # ya que era del estado previo a la sincronización.
                    return 
                except Exception as e:
                    self._report_error(report, f"Telegram rechazó el Webhook: {str(e)}")
            else:
                self._report_info(report, f"Webhook ya está sincronizado en: {status.url}")
            
            # Si llegamos aquí y hay un error, es porque ya estaba sincronizado pero sigue fallando
            if status.last_error_message:
                self._report_error(report, f"Telegram reporta fallo persistente en el Webhook: {status.last_error_message}")
                self._report_info(report, "💡 Sugerencia: Verifique que el túnel esté activo y que el servidor acepte conexiones.")
                
        except Exception as e:
            self._report_error(report, f"Fallo de conexión con Telegram: {e}")

    async def _validate_mcp(self, report: ValidationReport):
        """Valida los servidores MCP y reporta sugerencias de reparación."""
        self._report_info(report, "Verificando ecosistema de servidores MCP")
        try:
            mcp_results = await self.mcp_validator.validate_servers()
            for name, is_ok, suggestion in mcp_results:
                if is_ok:
                    self._report_info(report, f"MCP '{name}': Conectado/Disponible {suggestion}")
                else:
                    self._report_error(report, f"MCP '{name}': NO DISPONIBLE. {suggestion}")
        except Exception as e:
            self._report_error(report, f"Fallo crítico validando MCPs: {e}")
