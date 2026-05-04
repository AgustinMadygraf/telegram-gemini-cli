"""
Path: src/use_cases/ports/interfaces.py
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from src.entities.ai import AIResponse
from src.entities.ai_session import AISession
from src.entities.network import WebhookStatus
from src.entities.chat import ChatMessage

class LoggerPort(ABC):
    @abstractmethod
    def info(self, msg: str) -> None:
        """Loguea un mensaje informativo."""
        pass

    @abstractmethod
    def error(self, msg: str) -> None:
        """Loguea un mensaje de error."""
        pass

    @abstractmethod
    def debug(self, msg: str) -> None:
        """Loguea un mensaje de depuración."""
        pass

    @abstractmethod
    def warning(self, msg: str) -> None:
        """Loguea una advertencia."""
        pass

    @abstractmethod
    def critical(self, msg: str) -> None:
        """Loguea un fallo crítico del sistema."""
        pass

class AIEngineGateway(ABC):
    @abstractmethod
    async def ask(self, prompt: str, session: Optional[AISession] = None, attachments: List[str] = None) -> AIResponse:
        """Envia un prompt a la IA."""
        pass

    @abstractmethod
    async def reset(self, session: Optional[AISession] = None) -> bool:
        """Reinicia el contexto de la sesión."""
        pass

    @abstractmethod
    async def get_mcp_info(self) -> str:
        """Obtiene información sobre el estado de los servidores MCP desde la perspectiva de la IA."""
        pass

class MessagePresenter(ABC):
    @abstractmethod
    def format_response(self, response: AIResponse) -> List[str]:
        """Transforma una respuesta de la IA en mensajes formateados."""
        pass

class MessageGateway(ABC):
    @abstractmethod
    async def send_message(self, chat_id: int, text: str, parse_mode: Optional[str] = None) -> bool:
        """Envía un mensaje a un chat específico."""
        pass

    @abstractmethod
    async def set_typing(self, chat_id: int) -> None:
        """Activa el estado de 'escribiendo'."""
        pass

class FileGateway(ABC):
    @abstractmethod
    async def get_file_path(self, file_id: str) -> str:
        """Obtiene la ruta relativa de un archivo."""
        pass

    @abstractmethod
    async def download_file(self, file_path: str, destination: str) -> bool:
        """Descarga un archivo a una ruta local."""
        pass

class WebAdminGateway(ABC):
    @abstractmethod
    async def get_webhook_status(self) -> WebhookStatus:
        """Consulta el estado del webhook."""
        pass

    @abstractmethod
    async def set_webhook(self, url: str, secret_token: Optional[str] = None) -> bool:
        """Configura la URL del webhook."""
        pass

class CredentialValidatorGateway(ABC):
    @abstractmethod
    async def validate(self) -> bool:
        """Valida las credenciales."""
        pass

class MCPValidatorGateway(ABC):
    @abstractmethod
    async def validate_servers(self) -> List[Tuple[str, bool, str]]:
        """Valida los servidores MCP."""
        pass

class TunnelGateway(ABC):
    @abstractmethod
    async def validate_tunnel(self, url: Optional[str] = None) -> bool:
        """Verifica que el túnel esté saludable."""
        pass

    @abstractmethod
    def start_tunnel(self) -> None:
        pass

    @abstractmethod
    def stop_tunnel(self) -> None:
        pass

class ShellGateway(ABC):
    @abstractmethod
    async def execute(self, args: List[str], env: Optional[dict] = None, cwd: Optional[str] = None, timeout: float = 30.0, logger: Optional[LoggerPort] = None) -> Tuple[int, str, str]:
        """Ejecuta un comando en el sistema."""
        pass

class FileSystemGateway(ABC):
    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def write_text(self, path: str, content: str) -> None:
        pass

    @abstractmethod
    def ensure_dir(self, path: str) -> None:
        pass

    @abstractmethod
    def read_text(self, path: str) -> str:
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        pass

    @abstractmethod
    def copy_directory(self, src: str, dst: str, ignore_patterns: List[str] = None) -> None:
        """Copia un directorio completo recursivamente."""
        pass

    @abstractmethod
    def remove_directory(self, path: str) -> None:
        """Elimina un directorio y todo su contenido."""
        pass

    @abstractmethod
    def get_absolute_path(self, path: str) -> str:
        """Convierte una ruta a su versión absoluta."""
        pass

class MarkdownConverterPort(ABC):
    @abstractmethod
    def to_html(self, text: str) -> str:
        pass

class ChatHistoryGateway(ABC):
    @abstractmethod
    async def save_message(self, message: ChatMessage) -> None:
        pass

    @abstractmethod
    async def get_recent_history(self, chat_id: int, limit: int = 10) -> List[ChatMessage]:
        pass

class GeminiConfigGateway(ABC):
    @abstractmethod
    def get_include_directories(self) -> List[str]:
        """Obtiene la lista de directorios externos que deben incluirse en el sandbox."""
        pass
