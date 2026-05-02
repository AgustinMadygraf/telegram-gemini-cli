"""
Path: src/use_cases/ports/interfaces.py
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from src.entities.ai import AIResponse
from src.entities.network import WebhookStatus

class AIEngineGateway(ABC):
    @abstractmethod
    async def ask(self, prompt: str) -> AIResponse:
        """Envia un prompt a la IA y devuelve su respuesta."""
        pass

    @abstractmethod
    async def reset(self) -> bool:
        """Reinicia el contexto de la sesión actual."""
        pass

class MessagePresenter(ABC):
    @abstractmethod
    def format_response(self, response: AIResponse) -> List[str]:
        """Transforma una respuesta de la IA en uno o varios mensajes formateados para la plataforma destino."""
        pass

class MessengerGateway(ABC):
    @abstractmethod
    async def send_message(self, chat_id: int, text: str, parse_mode: Optional[str] = None) -> bool:
        """Envía un mensaje a un chat específico."""
        pass

    @abstractmethod
    async def set_typing(self, chat_id: int) -> None:
        """Activa el estado de 'escribiendo' en el chat."""
        pass

    @abstractmethod
    async def get_webhook_status(self) -> WebhookStatus:
        """Consulta el estado actual del webhook en el proveedor."""
        pass

    @abstractmethod
    async def set_webhook(self, url: str, secret_token: Optional[str] = None) -> bool:
        """Configura la URL del webhook en el proveedor."""
        pass

class CredentialValidatorGateway(ABC):
    @abstractmethod
    async def validate(self) -> bool:
        """Valida que las credenciales sean correctas."""
        pass

class TunnelGateway(ABC):
    @abstractmethod
    async def validate_tunnel(self) -> bool:
        """Verifica que el túnel esté activo y saludable."""
        pass

    @abstractmethod
    def start_tunnel(self) -> None:
        """Inicia el proceso del túnel en segundo plano."""
        pass

    @abstractmethod
    def stop_tunnel(self) -> None:
        """Detiene el proceso del túnel."""
        pass

class ShellGateway(ABC):
    @abstractmethod
    async def execute(self, args: List[str]) -> Tuple[int, str, str]:
        """Ejecuta un comando en el sistema y devuelve (return_code, stdout, stderr)."""
        pass

class FileSystemGateway(ABC):
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Verifica si un path existe en el sistema de archivos."""
        pass
