"""
Path: src/use_cases/services/output_sanitizer.py
"""

import re
from typing import List, Optional
from src.use_cases.ports.interfaces import LoggerPort

class OutputSanitizerService:
    """
    Servicio de Dominio encargado de limpiar el ruido de infraestructura 
    de las respuestas generadas por los motores de IA.
    """
    
    def __init__(self):
        # Patrones de expresiones regulares para ruidos técnicos persistentes
        self.noise_patterns = [
            r"ripgrep is not available",
            r"falling back to greptool",
            r"ide fetch failed",
            r"failed to connect to ide",
            r"YOLO mode is enabled", # Nuevo: Filtra el aviso de modo yolo de la CLI
            r"no previous sessions found",
            r"mcp issues detected",
            r"run /mcp list",
            r"run /ide install",
            r"typeerror: fetch failed",
            r"econnrefused",
            r"error: connect",
            r"\[error\]",
            r"\[info\]",
            r"\[debug\]",
            r"at process\.",
            r"at object\.",
            r"at async",
            r"at node:internal",
            r"at StreamableHTTPClientTransport",
            r"at Gaxios\.",
            r"at retryWithBackoff",
            r"at GeminiChat\.",
            r"\(node:internal/.*\)",
            r"node_modules",
            r"ide-connection-utils",
            r"\[ideclient\]",
            r"\[ideconnectionutils\]",
            r"errno: -\d+",
            r"code: '.*'",
            r"syscall: '.*'",
            r"address: '.*'",
            r"port: \d+",
            r"error executing tool",
            r"path not in workspace",
            r"resolves outside the allowed workspace",
            r"file not found\.",
            r"GaxiosError:",
            r"backendError",
            r"status: \d{3}",
            r"statusText:",
            r"responseURL:",
            r"server: 'ESF'",
            r"server-timing:",
            r"x-goog-api-client:",
            # Gaxios HTTP dump (config, headers, response)
            r"config:\s*\{",
            r"response:\s*\{",
            r"request:\s*\{",
            r"headers:\s*\{",
            r"^\s*url:\s*'",
            r"^\s*method:\s*'",
            r"^\s*params:\s*",
            r"^\s*responseType:",
            r"^\s*body:\s*'",
            r"^\s*signal:\s*",
            r"^\s*retry:\s*",
            r"^\s*paramsSerializer:",
            r"^\s*validateStatus:",
            r"^\s*errorRedactor:",
            r"^\s*data:\s*'",
            r"^\s*error:\s*undefined",
            r"Symbol\(gaxios",
            r"'Content-Type':",
            r"'User-Agent':",
            r"Authorization:",
            r"REDACTED",
            r"'alt-svc':",
            r"'content-length':",
            r"'content-type':",
            r"^\s*date:",
            r"^\s*vary:",
            r"x-cloud",
            r"x-content-type",
            r"x-frame-options",
            r"x-xss-protection",
            r"AbortSignal",
            r"^\s*\[Object\]",
            r"^\s*\[AbortSignal\]",
            r"^\s*\[Function:",
            r"^\s*at\s+.*$" # Captura cualquier línea que parezca un stack trace (ej: "  at func (file:line)")
        ]
        
        # Compilar patrones para mejorar rendimiento
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.noise_patterns]

    def sanitize(self, text: str, logger: Optional[LoggerPort] = None) -> str:
        """
        Filtra ruidos técnicos, caracteres de control y bloques vacíos usando regex.
        Si se provee un logger, registra el ruido filtrado para depuración.
        """
        if not text:
            return ""

        # 1. Eliminar caracteres de control ASCII (no imprimibles)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 2. Eliminar secuencias literales de control que a veces el CLI escapa
        text = text.replace('^B', '')

        lines = text.splitlines()
        clean_lines = []
        filtered_count = 0

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
                
            # Filtrar si coincide con algún patrón de ruido
            is_noise = any(pattern.search(trimmed) for pattern in self.compiled_patterns)
            
            # Filtrar líneas que son solo restos de JSON o cierres de bloques accidentales
            is_fragment = trimmed in ["}", "},", "]", "],", "{", "["]

            if is_noise or is_fragment:
                filtered_count += 1
                if logger:
                    logger.debug(f"🧹 Filtrado por sanitizer: {trimmed}")
                continue
                
            clean_lines.append(trimmed)

        if logger and filtered_count > 0:
            logger.debug(f"📊 Sanitizer: {filtered_count} líneas de ruido eliminadas.")

        # 3. Reensamblar
        result = "\n".join(clean_lines).strip()
        
        # 4. Salvaguarda final: si solo queda ruido residual insignificante
        if len(result) < 2 and result not in ["?", "!", "i", "y", "n"]:
            return ""
            
        return result
