"""
Path: src/infrastructure/setting/logger.py
"""

import logging
import sys
import os
from contextvars import ContextVar
from typing import Optional
from src.use_cases.ports.interfaces import LoggerPort

# Variable de contexto global para el ID de rastreo
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)

def setup_logger():
    # Formato profesional: Timestamp [LEVEL] [TRACE-ID] logger: message
    log_format = '%(asctime)s [%(levelname)s] [%(correlation_id)s] %(name)s: %(message)s'
    
    # Filtro para inyectar el correlation_id en cada registro
    class CorrelationFilter(logging.Filter):
        def filter(self, record):
            record.correlation_id = correlation_id.get() or "SYSTEM"
            return True

    handler = logging.StreamHandler(sys.stdout)
    handler.terminator = '\r\n'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[handler]
    )
    
    # Aplicar el filtro al handler raíz
    for handler in logging.getLogger().handlers:
        handler.addFilter(CorrelationFilter())
    # Silenciar logs ruidosos de librerías externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("python-telegram-bot").setLevel(logging.WARNING)

class StandardLoggerAdapter(LoggerPort):
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)
