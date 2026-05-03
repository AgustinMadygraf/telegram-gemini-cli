"""
Path: src/infrastructure/logging/console_logger.py
"""

import logging
import sys
from src.use_cases.ports.interfaces import LoggerPort

class ConsoleLoggerAdapter(LoggerPort):
    def __init__(self):
        self.logger = logging.getLogger("telegram_gemini_bridge")
        self.logger.setLevel(logging.DEBUG)
        
        # Formateador estético
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def critical(self, msg: str) -> None:
        self.logger.critical(msg)
