from abc import ABC, abstractmethod
from src.domain.entities import ChatMessage, AIResponse

class AIEngineInterface(ABC):
    @abstractmethod
    async def ask(self, prompt: str) -> AIResponse:
        """Envia un prompt a la IA y devuelve su respuesta."""
        pass

    @abstractmethod
    async def reset(self) -> bool:
        """Reinicia el contexto de la sesión actual."""
        pass

class MessagingProviderInterface(ABC):
    @abstractmethod
    async def send_message(self, chat_id: int, text: str) -> bool:
        """Envía un mensaje al usuario."""
        pass

    @abstractmethod
    async def set_typing(self, chat_id: int) -> None:
        """Activa el estado de 'escribiendo' en el chat."""
        pass
