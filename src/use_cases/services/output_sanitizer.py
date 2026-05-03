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
    
    def __init__(self, noise_keywords: Optional[List[str]] = None):
        # Lista exhaustiva de ruidos técnicos observados en logs reales
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
            "error: connect",
            "typeerror: fetch failed",
            "error executing tool",
            "path not in workspace",
            "attempted path",
            "resolves outside the allowed workspace",
            "file not found.",
            "run /mcp list",
            "run /ide install"
        ]

    def sanitize(self, text: str) -> str:
        """
        Filtra ruidos técnicos, caracteres de control y bloques vacíos.
        Retorna una cadena limpia o vacía si no hay contenido útil.
        """
        if not text:
            return ""

        # 1. Eliminar caracteres de control ASCII (no imprimibles)
        # Esto elimina ^B (\x02), campanas (\x07), etc.
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Eliminar secuencias literales '^B' que a veces aparecen en el stream
        text = text.replace('^B', '')

        lines = text.splitlines()
        clean_lines = []

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
                
            # Saltar si la línea contiene ruido técnico
            lower_line = trimmed.lower()
            if any(kw in lower_line for kw in self.noise_keywords):
                continue
            
            # Saltar líneas que son solo caracteres de cierre de JSON/bloques
            if trimmed in ["}", "},", "]", "],", "{", "["]:
                continue
                
            # Si pasa los filtros, la guardamos (manteniendo el indentado original si se desea, 
            # pero aquí optamos por un trim para evitar bloques vacíos extraños)
            clean_lines.append(trimmed)

        # 3. Reensamblar
        result = "\n".join(clean_lines).strip()
        
        # 4. Salvaguarda final: si solo queda ruido residual insignificante (ej: ".")
        if len(result) < 2 and result not in ["?", "!", "i"]:
            return ""
            
        return result
