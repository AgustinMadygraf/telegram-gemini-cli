import asyncio
import os
from src.domain.interfaces import AIEngineInterface, CredentialValidatorInterface
from src.domain.entities import AIResponse
import logging

logger = logging.getLogger(__name__)

class GeminiCLIAdapter(AIEngineInterface, CredentialValidatorInterface):
    def __init__(self, binary_path: str = "/usr/local/bin/gemini"):
        self.binary_path = binary_path

    async def validate(self) -> bool:
        """Verifica que el binario de gemini exista y sea ejecutable."""
        if not os.path.exists(self.binary_path):
            logger.error(f"El binario de Gemini no se encuentra en: {self.binary_path}")
            return False
        
        try:
            process = await asyncio.create_subprocess_exec(
                self.binary_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            if process.returncode == 0:
                logger.info(f"Gemini CLI validado. Versión: {stdout.decode().strip()}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al validar Gemini CLI: {e}")
            return False

    async def ask(self, prompt: str) -> AIResponse:
        try:
            # Ejecutamos gemini con el prompt y persistencia de sesión
            process = await asyncio.create_subprocess_exec(
                self.binary_path,
                "-p", prompt,
                "--resume", "latest",
                "--output-format", "text",
                "--approval-mode", "auto_edit",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return AIResponse(text=stdout.decode().strip(), success=True)
            else:
                return AIResponse(
                    text="", 
                    success=False, 
                    error_message=stderr.decode().strip()
                )
        except Exception as e:
            return AIResponse(text="", success=False, error_message=str(e))

    async def reset(self) -> bool:
        # En la CLI actual, 'reset' podría ser simplemente no pasar --resume 
        # o borrar la sesión 'latest'. Por simplicidad, aquí simulamos éxito.
        # En el futuro se puede implementar 'gemini --delete-session latest'
        return True
