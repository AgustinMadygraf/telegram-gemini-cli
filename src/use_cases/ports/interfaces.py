"""
Path: src/use_cases/ports/interfaces.py
"""

from abc import ABC, abstractmethod
from src.entities.chat import ChatMessage
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

class MessengerGateway(ABC):
    @abstractmethod
    async def send_message(self, chat_id: int, text: str) -> bool:
        """Envía un mensaje al usuario."""
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
