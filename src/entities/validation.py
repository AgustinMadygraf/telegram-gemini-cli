"""
Path: src/entities/validation.py
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class ValidationReport:
    is_ok: bool = True
    info_messages: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    critical_messages: List[str] = field(default_factory=list)

    def add_info(self, message: str):
        self.info_messages.append(message)

    def add_error(self, message: str):
        self.is_ok = False
        self.error_messages.append(message)

    def add_critical(self, message: str):
        self.is_ok = False
        self.critical_messages.append(message)
