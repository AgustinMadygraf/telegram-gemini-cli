"""
Path: src/interface_adapters/gateways/ai_factory.py
"""

from src.use_cases.ports.interfaces import (
    AIEngineGateway, 
    CredentialValidatorGateway, 
    ShellGateway, 
    FileSystemGateway, 
    LoggerPort,
    AIConfigGateway
)
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.interface_adapters.gateways.gemini_config_adapter import GeminiLocalConfigAdapter
from src.use_cases.services.output_sanitizer import OutputSanitizerService
from src.use_cases.services.credential_manager import CredentialSyncService

class AIEngineFactory:
    @staticmethod
    def create_engine(
        provider: str,
        shell: ShellGateway,
        fs: FileSystemGateway,
        logger: LoggerPort,
        sanitizer: OutputSanitizerService,
        credential_service: CredentialSyncService,
        config: dict
    ) -> AIEngineGateway:
        """
        Crea una instancia del motor de IA basado en el proveedor configurado.
        """
        if provider == "gemini_cli":
            # Instanciar proveedor de configuración específico para Gemini
            config_gateway = GeminiLocalConfigAdapter(fs=fs, logger=logger)
            
            return GeminiCLIAdapter(
                shell=shell,
                fs=fs,
                logger=logger,
                sanitizer=sanitizer,
                credential_service=credential_service,
                config_gateway=config_gateway,
                binary_path=config.get("gemini_binary_path"),
                auth_method=config.get("gemini_auth_method"),
                api_key=config.get("gemini_api_key"),
                vertex_project=config.get("vertex_project_id"),
                vertex_location=config.get("vertex_location"),
                workspace_path=config.get("gemini_workspace")
            )
        
        elif provider == "ollama":
            # Aquí se instanciaría el OllamaAdapter en el futuro
            raise NotImplementedError("El proveedor 'ollama' aún no está implementado.")
        
        else:
            raise ValueError(f"Proveedor de IA desconocido: {provider}")

    @staticmethod
    def create_validator(engine: AIEngineGateway) -> CredentialValidatorGateway:
        """
        Retorna el validador asociado al motor.
        """
        if isinstance(engine, CredentialValidatorGateway):
            return engine
        raise ValueError("El motor de IA proporcionado no soporta validación de sistema.")
