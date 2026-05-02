"""
Path: src/interface_adapters/gateways/gemini_gateway.py
"""

from src.use_cases.ports.interfaces import (
    AIEngineGateway, 
    CredentialValidatorGateway,
    ShellGateway,
    FileSystemGateway
)
from src.entities.ai import AIResponse

class GeminiCLIAdapter(AIEngineGateway, CredentialValidatorGateway):
    def __init__(
        self, 
        shell: ShellGateway, 
        fs: FileSystemGateway,
        binary_path: str = "/usr/local/bin/gemini"
    ):
        self.shell = shell
        self.fs = fs
        self.binary_path = binary_path

    async def validate(self) -> bool:
        """Valida la existencia y ejecución del binario delegando al sistema."""
        if not self.fs.exists(self.binary_path):
            return False
        
        try:
            return_code, _, _ = await self.shell.execute([self.binary_path, "--version"])
            return return_code == 0
        except Exception:
            return False

    async def ask(self, prompt: str) -> AIResponse:
        """Ejecuta una consulta al CLI de Gemini delegando la ejecución al shell."""
        try:
            args = [
                self.binary_path,
                "-p", prompt,
                "--resume", "latest",
                "--output-format", "text",
                "--approval-mode", "auto_edit"
            ]
            
            return_code, stdout, stderr = await self.shell.execute(args)

            if return_code == 0:
                return AIResponse(text=stdout, success=True)
            else:
                return AIResponse(
                    text="", 
                    success=False, 
                    error_message=stderr
                )
        except Exception as e:
            return AIResponse(text="", success=False, error_message=str(e))

    async def reset(self) -> bool:
        """Reinicia el contexto."""
        return True
