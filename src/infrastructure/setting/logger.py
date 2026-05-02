"""
Path: src/infrastructure/setting/logger.py
"""

import logging
import sys
from src.use_cases.ports.interfaces import LoggerPort

def setup_logger():
    """Configuración global del logger para la aplicación."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
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
