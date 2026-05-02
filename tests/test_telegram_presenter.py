import pytest
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.entities.ai import AIResponse

def test_presenter_escapes_normal_text():
    presenter = TelegramPresenter()
    response = AIResponse(text="Hello. This is a test! (v1.0)", success=True)
    formatted = presenter.format_response(response)
    
    # Dot, exclamation and parenthesis should be escaped
    assert "Hello\\. This is a test\\! \\(v1\\.0\\)" in formatted[0]

def test_presenter_preserves_code_blocks():
    presenter = TelegramPresenter()
    code = "```python\nprint('hello')\n```"
    response = AIResponse(text=f"Check this code:\n{code}", success=True)
    formatted = presenter.format_response(response)
    
    # Normal text should be escaped, code block preserved
    assert "Check this code\\:" in formatted[0]
    assert "```\npython\nprint('hello')\n```" in formatted[0]

def test_presenter_handles_error():
    presenter = TelegramPresenter()
    response = AIResponse(text="", success=False, error_message="Something went wrong!")
    formatted = presenter.format_response(response)
    
    assert "❌ *Error de IA*" in formatted[0]
    assert "Something went wrong\\!" in formatted[0]

def test_presenter_chunks_long_text():
    presenter = TelegramPresenter(max_length=10)
    response = AIResponse(text="0123456789ABCDEF", success=True)
    formatted = presenter.format_response(response)
    
    assert len(formatted) == 2
    assert formatted[0] == "0123456789"
    assert formatted[1] == "ABCDEF"
