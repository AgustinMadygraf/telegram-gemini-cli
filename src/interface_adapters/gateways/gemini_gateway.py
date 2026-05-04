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
from src.entities.ai_session import AISession
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

    def _get_env_for_session(self, session: Optional[AISession]) -> dict:
        """Genera el entorno aislado y asegura la sincronización de credenciales."""
        # Si no hay sesión, usamos una por defecto 'default'
        safe_id = session.safe_id if session else "default"
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
            env = self._get_env_for_session(AISession(id="system_check"))
            
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
            
            combined_output = f"{stdout} {stderr}".lower()

            # 3. Errores críticos de autenticación/configuración → FATAL (bloquean arranque)
            critical_errors = ["command not found", "fatal error", "invalid api key", "authentication failed"]
            if any(err in combined_output for err in critical_errors):
                self.logger.error(f"❌ Error crítico detectado en la salida de Gemini: {sanitized_stdout} {sanitized_stderr}")
                return False

            # 4. Errores transitorios del backend (500, timeouts) → WARNING (permiten arranque)
            transient_indicators = ["status: 500", "internal error", "timeout"]
            is_transient = any(ind in combined_output for ind in transient_indicators) or return_code == -1
            
            if return_code != 0:
                if is_transient:
                    self.logger.warning(f"⚠️ Error transitorio en validación (Código {return_code}). El backend de Google puede estar inestable. Continuando arranque.")
                    return True
                self.logger.warning(f"⚠️  Error en validación Gemini CLI (Código {return_code}): {sanitized_stderr}")
                return False

            return True
        except Exception as e:
            self.logger.error(f"❌ Excepción en validador Gemini: {str(e)}")
            return False

    async def ask(
        self, 
        prompt: str, 
        session: Optional[AISession] = None, 
        attachments: List[str] = None
    ) -> AIResponse:
        """
        Envía un prompt al CLI de Gemini dentro de un entorno aislado.
        """
        env = self._get_env_for_session(session)
        
        # Obtener argumentos extra desde el proveedor de configuración
        include_dirs = self.config_gateway.get_include_directories()
        extra_args = []
        for path in include_dirs:
            extra_args.extend(["--include-directories", path])

        # --sandbox aísla el filesystem e impide acceso a directorios externos (MCPs).
        # Solo se activa si no hay include-directories que requieran acceso externo.
        args = [self.binary_path, "--prompt", prompt, "--approval-mode", "yolo"]
        if not extra_args:
            args.append("--sandbox")
        
        # Si hay sesión, intentamos resumirla
        if session:
            args.append("--resume")

        if attachments:
            args.extend(attachments)

        try:
            
            # Log de depuración para ver los argumentos finales
            self.logger.debug(f"📝 Comando Gemini: {' '.join(args + extra_args)}")

            return_code, stdout, stderr = await self.shell.execute(
                args + extra_args, 
                env=env, 
                cwd=self.workspace_path, 
                timeout=180.0,
                line_filter=self.sanitizer.noise_patterns
            )

            # Sanitizar y verificar
            sanitized_text = self.sanitizer.sanitize(stdout, logger=self.logger)
            
            if not sanitized_text:
                if stdout:
                    self.logger.debug("🔍 [DEBUG RAW OUTPUT] La respuesta fue vaciada. Contenido original:")
                    self.logger.debug("-" * 40)
                    self.logger.debug(stdout)
                    self.logger.debug("-" * 40)
                return AIResponse(text="", success=False, error_message="Respuesta vacía tras sanitización")

            if return_code == 0:
                return AIResponse(text=sanitized_text, success=True)
            else:
                # Manejo específico de fallos de sesión para reintentar sin --resume
                if session and ("--resume" in stderr.lower() or "no session" in stderr.lower()):
                    self.logger.info(f"🔄 Reintentando sin --resume para sesión {session.id}")
                    args.remove("--resume")
                    return_code, stdout, stderr = await self.shell.execute(
                        args + extra_args, 
                        env=env, 
                        cwd=self.workspace_path, 
                        timeout=180.0,
                        line_filter=self.sanitizer.noise_patterns
                    )
                    if return_code == 0:
                        return AIResponse(text=self.sanitizer.sanitize(stdout, logger=self.logger), success=True)

                # Si falló definitivamente, devolvemos el error sanitizado
                sanitized_stderr = self.sanitizer.sanitize(stderr)
                error_msg = sanitized_stderr or sanitized_text
                if not error_msg:
                    if "status: 500" in stderr or "status: 500" in stdout:
                        error_msg = "Error interno del servidor Gemini (500)"
                    else:
                        error_msg = f"Error de ejecución Gemini (Código {return_code})"
                
                return AIResponse(text="", success=False, error_message=error_msg)
        except Exception as e:
            self.logger.error(f"❌ Error inesperado en GeminiCLIAdapter: {e}")
            return AIResponse(text="", success=False, error_message=str(e))

    async def reset(self, session: Optional[AISession] = None) -> bool:
        """Reinicia el contexto borrando el directorio de la sesión."""
        safe_id = session.safe_id if session else "default"
        session_path = os.path.join(self.base_session_path, safe_id)
        try:
            # Usamos el sistema de archivos para borrar el directorio de forma recursiva
            self.fs.remove_directory(session_path)
            return True
        except Exception:
            return False

    async def get_mcp_info(self) -> str:
        """Obtiene el listado de servidores MCP configurados y su estado."""
        # Usamos una sesión especial para chequeos de sistema
        system_session = AISession(id="system_check")
        env = self._get_env_for_session(system_session)
        
        # ⚠️ mcp list NO soporta --include-directories
        args = [self.binary_path, "mcp", "list"]
        
        rc, stdout, stderr = await self.shell.execute(args, env=env)
        if rc != 0:
            return f"Error al listar MCP: {stderr or stdout}"
        return stdout
