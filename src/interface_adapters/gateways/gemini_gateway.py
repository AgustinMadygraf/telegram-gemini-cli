"""
Path: src/interface_adapters/gateways/gemini_gateway.py
"""

import os
from typing import Optional, List
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
        binary_path: str = "/usr/local/bin/gemini",
        auth_method: str = "api_key",
        api_key: Optional[str] = None,
        vertex_project: Optional[str] = None,
        vertex_location: str = "us-central1",
        workspace_path: Optional[str] = None
    ):
        self.shell = shell
        self.fs = fs
        self.binary_path = binary_path
        self.auth_method = auth_method
        self.api_key = api_key
        self.vertex_project = vertex_project
        self.vertex_location = vertex_location
        self.workspace_path = workspace_path if workspace_path and workspace_path.strip() else None
        
        if self.workspace_path:
            print(f"📂 Workspace configurado en: {self.workspace_path}")
            self.fs.ensure_dir(self.workspace_path)
        
        # Centralizamos en la nueva carpeta storage
        self.base_session_path = os.path.abspath("storage/sessions")
        self.fs.ensure_dir(self.base_session_path)

    def _get_env_for_session(self, session_id: str) -> dict:
        """Genera el entorno aislado y configura la autenticación según la estrategia."""
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("_", "-"))
        session_path = os.path.join(self.base_session_path, safe_id)
        self.fs.ensure_dir(session_path)
        
        env = {
            "GEMINI_CLI_HOME": session_path,
            "PATH": os.environ.get("PATH", "")
        }
        
        if self.auth_method == "api_key" and self.api_key:
            env["GEMINI_API_KEY"] = self.api_key
            
        elif self.auth_method == "vertex_ai":
            env["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
            if self.vertex_project:
                env["GOOGLE_CLOUD_PROJECT"] = self.vertex_project
            env["GOOGLE_CLOUD_LOCATION"] = self.vertex_location
            
        elif self.auth_method == "google_auth":
            self._handle_google_auth_inheritance(session_path)
            
        return env

    def _handle_google_auth_inheritance(self, session_path: str):
        """
        Copia la configuración global de Gemini al entorno de la sesión 
        para heredar la identidad del usuario (OAuth, proyectos, etc).
        """
        global_config_dir = os.path.expanduser("~/.gemini")
        target_config_dir = os.path.join(session_path, ".gemini")
        
        if self.fs.exists(global_config_dir):
            import shutil
            try:
                # Si ya existe, lo borramos para asegurar una copia limpia y fresca
                if os.path.exists(target_config_dir):
                    shutil.rmtree(target_config_dir)
                
                print(f"🔑 Sincronizando credenciales desde {global_config_dir}")
                # Copiamos la carpeta entera para asegurar OAuth y settings
                shutil.copytree(
                    global_config_dir, 
                    target_config_dir, 
                    ignore=shutil.ignore_patterns("tmp*", "sessions*", "logs*", "antigravity*")
                )
                print(f"✅ Credenciales sincronizadas.")
            except Exception as e:
                print(f"⚠️  Error sincronizando credenciales: {e}")

    async def validate(self) -> bool:
        """
        Valida que el binario exista y que la autenticación sea funcional
        haciendo una consulta de prueba.
        """
        # 1. Validar existencia del binario
        if not self.fs.exists(self.binary_path):
            print(f"❌ Binario de Gemini no encontrado en: {self.binary_path}")
            return False

        # 2. Validar dependencias críticas (ripgrep)
        rc, _, _ = await self.shell.execute(["which", "rg"])
        if rc != 0:
            print("❌ Dependencia faltante: 'ripgrep' (rg) es necesario para el funcionamiento de Gemini CLI.")
            return False
        
        # 2. Validar autenticación (Deep Auth Check)
        try:
            # 2.1 Verificar existencia física de credenciales si usamos google_auth
            if self.auth_method == "google_auth":
                global_config_dir = os.path.expanduser("~/.gemini")
                if not self.fs.exists(global_config_dir):
                    print(f"❌ Error: No se encontraron credenciales en {global_config_dir}. Ejecute 'gemini --login' primero.")
                    return False

            # 2.2 Usamos una sesión especial de validación de sistema
            env = self._get_env_for_session("system_check")
            
            # Ejecutamos un ping mínimo
            args = [
                self.binary_path,
                "--sandbox",
                "-p", "hi",
                "--output-format", "text",
                "--approval-mode", "auto_edit"
            ]
            
            timeout_seconds = 90.0
            print(f"⌛ Validando credenciales de Gemini (Deep Auth Check - Máx {timeout_seconds}s)")
            
            # Para la validación, NO usamos el workspace para evitar errores si está vacío
            return_code, stdout, stderr = await self.shell.execute(args, env=env, cwd=None, timeout=timeout_seconds)
            
            sanitized_stdout = self._sanitize_output(stdout)
            sanitized_stderr = self._sanitize_output(stderr)

            if return_code != 0:
                print(f"⚠️  Error en validación Gemini CLI (Código {return_code}): {sanitized_stderr}")
                return False
            
            # 3. Validar sanidad de la salida (infraestructura)
            # Solo fallamos si hay errores críticos de ejecución o falta de comandos base.
            # Ignoramos avisos de "Ripgrep fallback" o fallos de conexión al IDE (VS Code).
            critical_errors = ["command not found", "fatal error", "invalid api key", "authentication failed"]
            if any(err in sanitized_stderr.lower() or err in sanitized_stdout.lower() for err in critical_errors):
                print(f"❌ Error crítico detectado en la salida de Gemini: {sanitized_stdout} {sanitized_stderr}")
                return False

            return True
        except Exception as e:
            print(f"❌ Excepción en validador Gemini: {str(e)}")
            return False

    def _sanitize_output(self, text: str) -> str:
        """Limpia el ruido de infraestructura (logs, stacktraces de Node, avisos de Ripgrep)."""
        lines = text.splitlines()
        clean_lines = []
        
        # Patrones de ruido conocidos
        noise_patterns = [
            "ripgrep is not",
            "falling back to greptool",
            "ide fetch failed",
            "failed to connect to ide",
            "no previous sessions found",
            "mcp issues detected",
            "[error]",
            "[info]",
            "    at ", # Stack traces de Node.js
            "  [cause]:"
        ]
        
        for line in lines:
            # Si la línea no contiene ninguno de los patrones de ruido, la mantenemos
            if not any(pattern in line.lower() for pattern in noise_patterns):
                clean_lines.append(line)
        
        return "\n".join(clean_lines).strip()

    async def ask(self, prompt: str, session_id: str = "latest") -> AIResponse:
        """Ejecuta una consulta al CLI de Gemini delegando la ejecución al shell con aislamiento."""
        return_code, stdout, stderr = -1, "", ""
        try:
            env = self._get_env_for_session(session_id)
            
            # Intentamos resumir la sesión anterior en el directorio aislado.
            args = [
                self.binary_path,
                "--sandbox",
                "-p", prompt,
                "--resume",
                "--output-format", "text",
                "--approval-mode", "auto_edit"
            ]
            
            return_code, stdout, stderr = await self.shell.execute(args, env=env, cwd=self.workspace_path, timeout=180.0)

            # Limpiamos el ruido tanto de stdout como de stderr (a veces Gemini manda logs por stdout)
            sanitized_stdout = self._sanitize_output(stdout)
            sanitized_stderr = self._sanitize_output(stderr)

            if return_code == 0:
                return AIResponse(text=sanitized_stdout, success=True)
            else:
                # Si falló por --resume, reintentamos sin él
                if "--resume" in stderr or "no session" in stderr.lower():
                    args.remove("--resume")
                    return_code, stdout, stderr = await self.shell.execute(args, env=env, cwd=self.workspace_path, timeout=180.0)
                    if return_code == 0:
                        return AIResponse(text=self._sanitize_output(stdout), success=True)

                return AIResponse(
                    text="", 
                    success=False, 
                    error_message=sanitized_stderr or sanitized_stdout or "Error desconocido"
                )
        except Exception as e:
            return AIResponse(text="", success=False, error_message=str(e))

    async def reset(self, session_id: str = "latest") -> bool:
        """Reinicia el contexto borrando el directorio de la sesión."""
        session_path = os.path.join(self.base_session_path, session_id)
        try:
            # Usamos el shell para borrar el directorio de forma recursiva
            await self.shell.execute(["rm", "-rf", session_path], cwd=self.workspace_path)
            return True
        except Exception:
            return False
