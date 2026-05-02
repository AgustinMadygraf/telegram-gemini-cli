"""
Path: src/interface_adapters/gateways/cloudflare_gateway.py
"""

from src.use_cases.ports.interfaces import TunnelGateway
import logging
import httpx

logger = logging.getLogger(__name__)

class CloudflareGateway(TunnelGateway):
    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url

    async def validate_tunnel(self) -> bool:
        """
        Verifica el estado del túnel. 
        En una implementación completa, esto consultaría la API de Cloudflare.
        """
        if not self.token:
            logger.warning("CLOUDFLARE_TOKEN no configurado. Se omitirá la validación profunda del túnel.")
            return True # No bloqueamos si no hay token, a menos que se requiera

        logger.info(f"Validando estado del túnel para la URL: {self.webhook_url}")
        
        # Simulación de validación de conectividad local del túnel
        try:
            # Aquí podríamos intentar verificar si el proceso cloudflared responde localmente
            # o si la API de Cloudflare reporta el túnel como 'HEALTHY'
            logger.info("Túnel Cloudflare detectado como activo (Simulado).")
            return True
        except Exception as e:
            logger.error(f"Fallo al validar el túnel de Cloudflare: {e}")
            return False
