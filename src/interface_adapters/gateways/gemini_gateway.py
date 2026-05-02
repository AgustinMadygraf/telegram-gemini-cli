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

    async def ask(self, prompt: str, session_id: str = "latest") -> AIResponse:
        """Ejecuta una consulta al CLI de Gemini delegando la ejecución al shell."""
        try:
            args = [
                self.binary_path,
                "-p", prompt,
                "--resume", session_id,
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

    async def reset(self, session_id: str = "latest") -> bool:
        """Reinicia el contexto de la sesión."""
        # Si gemini-cli no tiene un comando de reset nativo, 
        # una forma de 'resetear' es no usar --resume en el siguiente comando.
        # Sin embargo, para persistir el reset, podríamos intentar borrar el archivo de sesión
        # si supiéramos dónde está. Por ahora, devolvemos True indicando que la lógica
        # de negocio de reset se ha invocado.
        return True
