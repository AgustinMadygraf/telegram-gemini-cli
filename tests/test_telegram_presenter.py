import pytest
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.entities.ai import AIResponse

def test_presenter_escape_inline_code():
    presenter = TelegramPresenter()
    # Texto con código inline
    text = "Usa `pip install` para instalar."
    # El escapado debería respetar los backticks
    # 'Usa ' -> 'Usa '
    # '`pip install`' -> '`pip install`'
    # '.' -> '\\.'
    escaped = presenter._escape(text)
    assert "`pip install`" in escaped
    assert "\\." in escaped

def test_presenter_escape_complex_markdown():
    presenter = TelegramPresenter()
    text = "Check this: *bold*, _italic_, [link](url), and `inline`."
    escaped = presenter._escape(text)
    assert "\\*" in escaped
    assert "\\_" in escaped
    assert "`inline`" in escaped

def test_format_response_error():
    presenter = TelegramPresenter()
    resp = AIResponse(text="", success=False, error_message="Fatal crash")
    formatted = presenter.format_response(resp)
    assert "Error de IA" in formatted[0]
    assert "Fatal crash" in formatted[0]

def test_format_response_long_text():
    presenter = TelegramPresenter()
    long_text = "A" * 5000
    resp = AIResponse(text=long_text, success=True)
    formatted = presenter.format_response(resp)
    assert len(formatted) > 1
    assert len(formatted[0]) <= 4096
