import pytest
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.entities.ai import AIResponse

def test_presenter_converts_markdown_to_html():
    presenter = TelegramPresenter()
    # Texto con negritas y código
    text = "Hola **mundo** y `codigo`."
    resp = AIResponse(text=text, success=True)
    
    formatted = presenter.format_response(resp)
    
    # Verificamos que contenga etiquetas HTML
    assert "<b>mundo</b>" in formatted[0]
    assert "<code>codigo</code>" in formatted[0]

def test_presenter_sanitizes_unsupported_tags():
    presenter = TelegramPresenter()
    # Texto con un encabezado (no soportado directamente)
    text = "# Titulo\nTexto"
    resp = AIResponse(text=text, success=True)
    
    formatted = presenter.format_response(resp)
    
    # El h1 debería haberse convertido a negrita (según nuestra lógica de sanitize)
    assert "<b>Titulo</b>" in formatted[0]
    assert "<h1>" not in formatted[0]

def test_presenter_handles_long_text_fragmentation():
    presenter = TelegramPresenter()
    # Generamos un texto largo para forzar el chunking
    long_text = ("Este es un parrafo largo que se repetira muchas veces para testear. " * 100)
    resp = AIResponse(text=long_text, success=True)
    
    formatted = presenter.format_response(resp)
    
    assert len(formatted) >= 1
    for chunk in formatted:
        assert len(chunk) <= 4096

def test_presenter_formats_error_response():
    presenter = TelegramPresenter()
    resp = AIResponse(text="", success=False, error_message="Error <critico>")
    
    formatted = presenter.format_response(resp)
    
    assert "<b>Error de IA</b>" in formatted[0]
    # Verificamos el escapado de caracteres HTML en el mensaje de error
    assert "&lt;critico&gt;" in formatted[0]
