"""
Path: src/use_cases/ports/interfaces.py
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from src.entities.ai import AIResponse
from src.entities.network import WebhookStatus

class AIEngineGateway(ABC):
    @abstractmethod
    async def ask(self, prompt: str, session_id: Optional[str] = None, attachments: List[str] = None) -> AIResponse:
        """
        Envia un prompt a la IA y devuelve su respuesta.
        attachments: Lista de rutas locales a archivos adjuntos.
        """
        pass

    @abstractmethod
    async def reset(self, session_id: Optional[str] = None) -> bool:
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

    @abstractmethod
    async def get_file_path(self, file_id: str) -> str:
        """Obtiene la ruta relativa de un archivo en los servidores del proveedor."""
        pass

    @abstractmethod
    async def download_file(self, file_path: str, destination: str) -> bool:
        """Descarga un archivo desde el proveedor a una ruta local."""
        pass

class CredentialValidatorGateway(ABC):
    @abstractmethod
    async def validate(self) -> bool:
        """Valida que las credenciales sean correctas."""
        pass

class MCPValidatorGateway(ABC):
    @abstractmethod
    async def validate_servers(self) -> List[Tuple[str, bool, str]]:
        """
        Valida los servidores MCP configurados.
        Devuelve una lista de (nombre_servidor, es_valido, sugerencia_reparacion).
        """
        pass

class TunnelGateway(ABC):
    @abstractmethod
    async def validate_tunnel(self, url: Optional[str] = None) -> bool:
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
    async def execute(self, args: List[str], env: Optional[dict] = None, cwd: Optional[str] = None, timeout: float = 30.0) -> Tuple[int, str, str]:
        """Ejecuta un comando en el sistema y devuelve (return_code, stdout, stderr)."""
        pass

class FileSystemGateway(ABC):
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Verifica si un archivo o directorio existe."""
        pass

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        """Escribe contenido en un archivo."""
        pass

    @abstractmethod
    def ensure_dir(self, path: str) -> None:
        """Asegura que un directorio exista, creándolo si es necesario."""
        pass

class MarkdownConverterPort(ABC):
    @abstractmethod
    def to_html(self, text: str) -> str:
        """Convierte texto Markdown a HTML."""
        pass

from src.entities.chat import ChatMessage

class ChatHistoryGateway(ABC):
    @abstractmethod
    async def save_message(self, message: ChatMessage) -> None:
        """Guarda un mensaje en el historial persistente."""
        pass

    @abstractmethod
    async def get_recent_history(self, chat_id: int, limit: int = 10) -> List[ChatMessage]:
        """Recupera los últimos N mensajes de un chat."""
        pass

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
