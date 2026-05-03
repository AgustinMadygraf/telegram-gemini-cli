"""
Path: src/use_cases/services/output_sanitizer.py
"""

import re
from typing import List, Optional

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
            r"^\s*at\s+.*$" # Captura cualquier línea que parezca un stack trace (ej: "  at func (file:line)")
        ]
        
        # Compilar patrones para mejorar rendimiento
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.noise_patterns]

    def sanitize(self, text: str) -> str:
        """
        Filtra ruidos técnicos, caracteres de control y bloques vacíos usando regex.
        """
        if not text:
            return ""

        # 1. Eliminar caracteres de control ASCII (no imprimibles)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 2. Eliminar secuencias literales de control que a veces el CLI escapa
        text = text.replace('^B', '')

        lines = text.splitlines()
        clean_lines = []

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
                
            # Filtrar si coincide con algún patrón de ruido
            if any(pattern.search(trimmed) for pattern in self.compiled_patterns):
                continue
            
            # Filtrar líneas que son solo restos de JSON o cierres de bloques de código accidentales
            if trimmed in ["}", "},", "]", "],", "{", "["]:
                continue
                
            clean_lines.append(trimmed)

        # 3. Reensamblar
        result = "\n".join(clean_lines).strip()
        
        # 4. Salvaguarda final: si solo queda ruido residual insignificante
        if len(result) < 2 and result not in ["?", "!", "i", "y", "n"]:
            return ""
            
        return result
