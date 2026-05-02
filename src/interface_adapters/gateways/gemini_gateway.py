"""
Path: src/interface_adapters/gateways/gemini_gateway.py
"""

import os
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
        # Usamos una ruta persistente en el proyecto en lugar de /tmp
        self.base_session_path = os.path.abspath("sessions")
        self._ensure_base_path()

    def _ensure_base_path(self):
        """Asegura que el directorio de sesiones exista."""
        self.fs.ensure_dir(self.base_session_path)

    def _get_env_for_session(self, session_id: str) -> dict:
        """Genera el entorno aislado para la sesión."""
        # Sanitizar session_id para evitar Path Traversal
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("_", "-"))
        session_path = os.path.join(self.base_session_path, safe_id)
        return {"GEMINI_CLI_HOME": session_path}

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
        """Ejecuta una consulta al CLI de Gemini delegando la ejecución al shell con aislamiento."""
        try:
            env = self._get_env_for_session(session_id)
            
            # Intentamos resumir la sesión anterior en el directorio aislado.
            # Si es la primera vez, el CLI iniciará una nueva.
            args = [
                self.binary_path,
                "-p", prompt,
                "--resume",
                "--output-format", "text",
                "--approval-mode", "auto_edit"
            ]
            
            return_code, stdout, stderr = await self.shell.execute(args, env=env)

            if return_code == 0:
                return AIResponse(text=stdout, success=True)
            else:
                # Si falló por --resume (ej. primera vez), reintentamos sin él
                if "--resume" in stderr or "no session" in stderr.lower():
                    args.remove("--resume")
                    return_code, stdout, stderr = await self.shell.execute(args, env=env)
                    if return_code == 0:
                        return AIResponse(text=stdout, success=True)

                return AIResponse(
                    text="", 
                    success=False, 
                    error_message=stderr
                )
        except Exception as e:
            return AIResponse(text="", success=False, error_message=str(e))

    async def reset(self, session_id: str = "latest") -> bool:
        """Reinicia el contexto borrando el directorio de la sesión."""
        session_path = os.path.join(self.base_session_path, session_id)
        try:
            # Usamos el shell para borrar el directorio de forma recursiva
            await self.shell.execute(["rm", "-rf", session_path])
            return True
        except Exception:
            return False
