"""
Path: src/entities/network.py
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class WebhookStatus:
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    last_error_date: Optional[int] = None
    last_error_message: Optional[str] = None
    max_connections: Optional[int] = None
    ip_address: Optional[str] = None
