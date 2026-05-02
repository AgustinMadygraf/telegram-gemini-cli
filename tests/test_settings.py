import pytest
import os
from unittest.mock import patch
from src.infrastructure.setting.config import Settings
from src.infrastructure.setting.logger import setup_logger

def test_settings_load():
    # Forzamos valores vía entorno para el test
    with patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "ALLOWED_CHAT_IDS": "[123]",
        "GEMINI_AUTH_METHOD": "api_key"
    }):
        s = Settings()
        assert s.TELEGRAM_BOT_TOKEN == "test_token"
        assert s.ALLOWED_CHAT_IDS == [123]
        assert s.GEMINI_AUTH_METHOD == "api_key"

def test_logger_setup():
    setup_logger()
    import logging
    # Verificamos que el logger raíz o uno específico tenga nivel INFO (20)
    logger = logging.getLogger()
    assert logger.level >= logging.INFO
