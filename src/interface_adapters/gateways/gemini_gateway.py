"""
Path: src/interface_adapters/gateways/gemini_gateway.py
"""

import os
from typing import Optional, List
from src.use_cases.ports.interfaces import (
    AIEngineGateway, 
    CredentialValidatorGateway,
    ShellGateway,
    FileSystemGateway,
    LoggerPort,
    GeminiConfigGateway
)
from src.entities.ai import AIResponse
from src.use_cases.services.output_sanitizer import OutputSanitizerService
from src.use_cases.services.credential_manager import CredentialSyncService

class GeminiCLIAdapter(AIEngineGateway, CredentialValidatorGateway):
    def __init__(
        self, 
        shell: ShellGateway, 
        fs: FileSystemGateway,
        logger: LoggerPort,
        sanitizer: OutputSanitizerService,
        credential_service: CredentialSyncService,
        config_gateway: GeminiConfigGateway,
        binary_path: str = "gemini",
        auth_method: str = "api_key",
        api_key: Optional[str] = None,
        vertex_project: Optional[str] = None,
        vertex_location: str = "us-central1",
        workspace_path: Optional[str] = None
    ):
        self.shell = shell
        self.fs = fs
        self.logger = logger
        self.sanitizer = sanitizer
        self.credential_service = credential_service
        self.config_gateway = config_gateway
        self.binary_path = binary_path
        self.auth_method = auth_method
        self.api_key = api_key
        self.vertex_project = vertex_project
        self.vertex_location = vertex_location
        self.workspace_path = workspace_path if workspace_path and workspace_path.strip() else None
        
        if self.workspace_path:
            self.logger.info(f"📂 Workspace configurado en: {self.workspace_path}")
            self.fs.ensure_dir(self.workspace_path)
        
        # Centralizamos en la nueva carpeta storage
        self.base_session_path = self.fs.get_absolute_path("storage/sessions")
        self.fs.ensure_dir(self.base_session_path)

    def _get_env_for_session(self, session_id: str) -> dict:
        """Genera el entorno aislado y asegura la sincronización de credenciales."""
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("_", "-"))
        session_path = os.path.join(self.base_session_path, safe_id)
        self.fs.ensure_dir(session_path)
        
        # Delegamos la sincronización al servicio especializado
        if self.auth_method == "google_auth":
            self.credential_service.sync_credentials(session_path)
        
        env = os.environ.copy()
        env.update({
            "GEMINI_CLI_HOME": session_path,
            "PATH": os.environ.get("PATH", ""),
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor"
        })
        
        if self.auth_method == "api_key" and self.api_key:
            env["GEMINI_API_KEY"] = self.api_key
            
        elif self.auth_method == "vertex_ai":
            env["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
            if self.vertex_project:
                env["GOOGLE_CLOUD_PROJECT"] = self.vertex_project
            env["GOOGLE_CLOUD_LOCATION"] = self.vertex_location
            
        return env

    async def validate(self) -> bool:
        """
        Valida que el binario exista y que la autenticación sea funcional
        haciendo una consulta de prueba.
        """
        # 1. Validar existencia del binario
        if not self.fs.exists(self.binary_path):
            self.logger.error(f"❌ Binario de Gemini no encontrado en: {self.binary_path}")
            return False

        # 2. Validar dependencias críticas (ripgrep)
        rc, _, _ = await self.shell.execute(["which", "rg"])
        if rc != 0:
            self.logger.error("❌ Dependencia faltante: 'ripgrep' (rg) es necesario para el funcionamiento de Gemini CLI.")
            return False
        
        # 2. Validar autenticación (Deep Auth Check)
        try:
            # 2.1 Verificar existencia física de credenciales si usamos google_auth
            if self.auth_method == "google_auth":
                global_config_dir = os.path.expanduser("~/.gemini")
                if not self.fs.exists(global_config_dir):
                    self.logger.error(f"❌ Error: No se encontraron credenciales en {global_config_dir}. Ejecute 'gemini --login' primero.")
                    return False

            # 2.2 Usamos una sesión especial de validación de sistema
            env = self._get_env_for_session("system_check")
            
            # Ejecutamos un ping mínimo
            args = [
                self.binary_path,
                "--sandbox",
                "-p", "hi",
                "--output-format", "text",
                "--approval-mode", "yolo"
            ]
            
            timeout_seconds = 120.0
            self.logger.info(f"⌛ Validando credenciales de Gemini (Deep Auth Check - Máx {timeout_seconds}s)")
            
            # Para la validación, NO usamos el workspace para evitar errores si está vacío
            # Pasamos el logger para ver el progreso real en la CLI durante el arranque
            # Usamos los patrones de ruido del sanitizador para limpiar los logs del shell
            return_code, stdout, stderr = await self.shell.execute(
                args, 
                env=env, 
                cwd=None, 
                timeout=timeout_seconds, 
                logger=self.logger,
                line_filter=self.sanitizer.noise_patterns
            )
            
            sanitized_stdout = self.sanitizer.sanitize(stdout)
            sanitized_stderr = self.sanitizer.sanitize(stderr)

            if return_code != 0:
                self.logger.warning(f"⚠️  Error en validación Gemini CLI (Código {return_code}): {sanitized_stderr}")
                return False
            
            # 3. Validar sanidad de la salida (infraestructura)
            # Solo fallamos si hay errores críticos de ejecución o falta de comandos base.
            # Ignoramos avisos de "Ripgrep fallback" o fallos de conexión al IDE (VS Code).
            critical_errors = ["command not found", "fatal error", "invalid api key", "authentication failed"]
            if any(err in sanitized_stderr.lower() or err in sanitized_stdout.lower() for err in critical_errors):
                self.logger.error(f"❌ Error crítico detectado en la salida de Gemini: {sanitized_stdout} {sanitized_stderr}")
                return False

            return True
        except Exception as e:
            self.logger.error(f"❌ Excepción en validador Gemini: {str(e)}")
            return False

    async def ask(self, prompt: str, session_id: Optional[str] = None, attachments: List[str] = None) -> AIResponse:
        """Ejecuta una consulta al CLI de Gemini delegando la ejecución al shell con aislamiento."""
        return_code, stdout, stderr = -1, "", ""
        try:
            session_id = session_id or "latest"
            env = self._get_env_for_session(session_id)
            
            # Construcción de argumentos base
            args = [
                self.binary_path,
                "--sandbox",
                "-p", prompt,
                "--resume",
                "--output-format", "text",
                "--approval-mode", "yolo"
            ]
            
            # Añadir archivos adjuntos si existen
            if attachments:
                args.extend(attachments)
            
            # Obtener argumentos extra desde el proveedor de configuración
            include_dirs = self.config_gateway.get_include_directories()
            extra_args = []
            for path in include_dirs:
                extra_args.extend(["--include-directories", path])
            
            return_code, stdout, stderr = await self.shell.execute(
                args + extra_args, 
                env=env, 
                cwd=self.workspace_path, 
                timeout=180.0,
                line_filter=self.sanitizer.noise_patterns
            )

            # Sanitizamos ambos flujos
            sanitized_stdout = self.sanitizer.sanitize(stdout)
            sanitized_stderr = self.sanitizer.sanitize(stderr)

            if return_code == 0:
                # Si tenemos éxito, priorizamos la salida estándar sanitizada
                # Si stdout queda vacío tras sanitizar, pero stderr tiene contenido útil (raro en éxito), lo consideramos.
                result_text = sanitized_stdout or sanitized_stderr
                return AIResponse(text=result_text, success=True)
            else:
                # Manejo específico de fallos de sesión para reintentar sin --resume
                if "--resume" in stderr.lower() or "no session" in stderr.lower():
                    self.logger.info(f"🔄 Reintentando sin --resume para sesión {session_id}")
                    args.remove("--resume")
                    return_code, stdout, stderr = await self.shell.execute(
                        args, 
                        env=env, 
                        cwd=self.workspace_path, 
                        timeout=180.0,
                        line_filter=self.sanitizer.noise_patterns
                    )
                    if return_code == 0:
                        return AIResponse(text=self.sanitizer.sanitize(stdout), success=True)

                # Si falló definitivamente, devolvemos el error sanitizado
                # Si el error sanitizado queda vacío (por exceso de filtrado), usamos el original o un genérico
                error_msg = sanitized_stderr or sanitized_stdout
                if not error_msg:
                    # Si no hay nada tras sanitizar, pero hubo error, extraemos una pista del original
                    if "status: 500" in stderr or "status: 500" in stdout:
                        error_msg = "Error interno del servidor Gemini (500)"
                    else:
                        error_msg = f"Error de ejecución Gemini (Código {return_code})"
                
                return AIResponse(text="", success=False, error_message=error_msg)
        except Exception as e:
            return AIResponse(text="", success=False, error_message=str(e))

    async def reset(self, session_id: str = "latest") -> bool:
        """Reinicia el contexto borrando el directorio de la sesión."""
        session_path = os.path.join(self.base_session_path, session_id)
        try:
            # Usamos el sistema de archivos para borrar el directorio de forma recursiva
            self.fs.remove_directory(session_path)
            return True
        except Exception:
            return False

    async def get_mcp_info(self) -> str:
        """Obtiene el listado de servidores MCP configurados y su estado."""
        env = self._get_env_for_session("system_check")
        
        include_dirs = self.config_gateway.get_include_directories()
        extra_args = []
        for path in include_dirs:
            extra_args.extend(["--include-directories", path])

        args = [self.binary_path, "mcp", "list"]
        
        rc, stdout, stderr = await self.shell.execute(args + extra_args, env=env)
        if rc != 0:
            return f"Error al listar MCP: {stderr or stdout}"
        return stdout
