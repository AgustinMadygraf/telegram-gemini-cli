"""
Path: src/interface_adapters/gateways/gemini_gateway.py
"""

import asyncio
import os
from src.use_cases.ports.interfaces import AIEngineGateway, CredentialValidatorGateway
from src.entities.ai import AIResponse

class GeminiCLIAdapter(AIEngineGateway, CredentialValidatorGateway):
    def __init__(self, binary_path: str = "/usr/local/bin/gemini"):
        self.binary_path = binary_path

    async def validate(self) -> bool:
        """Valida la existencia y ejecución del binario de Gemini."""
        if not os.path.exists(self.binary_path):
            return False
        
        try:
            process = await asyncio.create_subprocess_exec(
                self.binary_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False

    async def ask(self, prompt: str) -> AIResponse:
        """Ejecuta una consulta al CLI de Gemini."""
        try:
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
        """Reinicia el contexto (implementación pendiente en CLI)."""
        return True
