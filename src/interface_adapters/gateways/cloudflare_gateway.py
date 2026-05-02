"""
Path: src/interface_adapters/gateways/cloudflare_gateway.py
"""

from src.use_cases.ports.interfaces import TunnelGateway

class CloudflareGateway(TunnelGateway):
    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url

    async def validate_tunnel(self) -> bool:
        """
        Verifica el estado del túnel. 
        Puro y silencioso. Si falla, lanza excepción o devuelve False.
        """
        if not self.token:
            # No logueamos, el caso de uso decidirá si esto es un error o advertencia.
            return False

        try:
            # Simulación de validación (en el futuro una llamada HTTP real)
            return True
        except Exception:
            return False
