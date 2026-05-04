"""
Path: src/entities/ai_session.py
"""

from dataclasses import dataclass
import re

@dataclass(frozen=True)
class AISession:
    """
    Entidad que representa una sesión aislada del motor de IA.
    Encapsula la validación del ID y la integridad de su estado.
    """
    id: str

    def __post_init__(self):
        # Validar que el ID sea seguro para usar como nombre de directorio
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.id):
            raise ValueError(f"ID de sesión inválido: {self.id}. Solo se permiten caracteres alfanuméricos, guiones y guiones bajos.")

    @property
    def safe_id(self) -> str:
        return self.id

    def __str__(self) -> str:
        return self.id
