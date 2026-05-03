"""
Path: src/use_cases/services/output_sanitizer.py
"""

from typing import List

class OutputSanitizerService:
    """
    Servicio de Dominio encargado de limpiar el ruido de infraestructura 
    de las respuestas generadas por los motores de IA.
    """
    
    def __init__(self, noise_keywords: List[str] = None):
        self.noise_keywords = noise_keywords or [
            "ripgrep is not",
            "falling back to greptool",
            "ide fetch failed",
            "failed to connect to ide",
            "no previous sessions found",
            "mcp issues detected",
            "[error]",
            "[info]",
            "at object.processresponse",
            "at node:internal",
            "node_modules",
            "undici",
            "at async",
            "ide-connection-utils",
            "[ideclient]",
            "[ideconnectionutils]",
            "errno:",
            "code:",
            "syscall:",
            "address:",
            "port:",
            "econnrefused",
            "[cause]",
            "[c",
            "error: connect",
            "typeerror: fetch failed",
            "at object.processresponse",
            "errno:",
            "syscall:"
        ]

    def sanitize(self, text: str) -> str:
        """
        Limpia un texto eliminando trazas de stack, logs de infraestructura
        y mensajes de error internos.
        """
        if not text:
            return ""
            
        lines = text.splitlines()
        clean_lines = []
        
        for line in lines:
            trimmed_line = line.strip()
            if not trimmed_line:
                continue
                
            # Regla 1: Stacktraces de Node.js / Python
            if trimmed_line.startswith("at ") or trimmed_line.startswith("at async") or trimmed_line.startswith("stdout>"):
                continue
                
            # Regla 2: Ruido de llaves/corchetes sueltos (típicos de volcados de error JSON)
            if trimmed_line in ["}", "{", "],", "],", "},", "["]:
                continue

            # Regla 3: Palabras clave de ruido
            if any(kw in trimmed_line.lower() for kw in self.noise_keywords):
                continue
                
            clean_lines.append(line)
        
        return "\n".join(clean_lines).strip()
