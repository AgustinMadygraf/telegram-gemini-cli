"""
Path: src/use_cases/system_validator.py
"""

from src.use_cases.ports.interfaces import (
    CredentialValidatorGateway, 
    WebAdminGateway,
    MessageGateway,
    TunnelGateway, 
    MCPValidatorGateway,
    LoggerPort
)
from src.entities.validation import ValidationReport
from typing import List, Optional

class SystemValidatorService:
    def __init__(
        self, 
        validators: List[CredentialValidatorGateway], 
        logger: LoggerPort, 
        messenger: MessageGateway,
        tunnel: TunnelGateway,
        mcp_validator: MCPValidatorGateway,
        web_admin: WebAdminGateway,
        webhook_url: str,
        secret_token: Optional[str] = None,
        admin_chat_id: Optional[int] = None
    ):
        self.validators = validators
        self.logger = logger
        self.messenger = messenger
        self.tunnel = tunnel
        self.mcp_validator = mcp_validator
        self.web_admin = web_admin
        self.webhook_url = webhook_url
        self.secret_token = secret_token
        self.admin_chat_id = admin_chat_id

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
                self._report_info(report, "⚠️  Túnel no detectado o token faltante. Se permite continuar en modo degradado.")
        else:
            self._report_info(report, "No se ha configurado un gestor de túneles.")

        # 3. Validar y Sincronizar Red (Webhook)
        if self.web_admin:
            await self._validate_network(report)
        
        # 4. Validar Ecosistema MCP
        if self.mcp_validator:
            await self._validate_mcp(report)
        
        if report.is_ok:
            self._report_info(report, "Sistema validado correctamente.")
        else:
            self._report_critical(report, "Se encontraron fallos críticos que impiden el arranque seguro.")
            if self.admin_chat_id:
                await self._send_alert_to_admin(report)
            
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
            status = await self.web_admin.get_webhook_status()
            
            if status.url != self.webhook_url or status.last_error_message:
                self._report_info(report, f"Sincronizando Webhook (Limpieza de estado): '{self.webhook_url}'")
                try:
                    await self.web_admin.set_webhook(
                        url=self.webhook_url, 
                        secret_token=self.secret_token
                    )
                    self._report_info(report, "Webhook sincronizado con éxito.")
                except Exception as e:
                    self._report_error(report, f"Telegram rechazó el Webhook: {str(e)}")
            else:
                self._report_info(report, f"Webhook ya está sincronizado en: {status.url}")
                
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

    async def _send_alert_to_admin(self, report: ValidationReport):
        """Envía una alerta consolidada al administrador vía Telegram."""
        header = "🚨 *FALLO CRÍTICO DE SISTEMA*\n\n"
        errors = "\n".join([f"❌ {msg}" for msg in report.error_messages])
        criticals = "\n".join([f"🔥 {msg}" for msg in report.critical_messages])
        
        message = f"{header}Se han detectado problemas que impiden el arranque:\n\n{errors}\n{criticals}\n\nRevisa los logs del servidor para más detalles."
        
        try:
            await self.messenger.send_message(
                chat_id=self.admin_chat_id,
                text=message,
                parse_mode="Markdown"
            )
            self.logger.info(f"Alerta enviada al administrador (ID: {self.admin_chat_id})")
        except Exception as e:
            self.logger.error(f"No se pudo enviar la alerta al administrador: {e}")
