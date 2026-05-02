import asyncio
from src.domain.interfaces import AIEngineInterface
from src.domain.entities import AIResponse

class GeminiCLIAdapter(AIEngineInterface):
    def __init__(self, binary_path: str = "/usr/local/bin/gemini"):
        self.binary_path = binary_path

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
