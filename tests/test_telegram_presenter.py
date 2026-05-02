import pytest
from unittest.mock import MagicMock
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.entities.ai import AIResponse
from src.use_cases.ports.interfaces import MarkdownConverterPort

@pytest.fixture
def mock_markdown():
    return MagicMock(spec=MarkdownConverterPort)

@pytest.fixture
def presenter(mock_markdown):
    return TelegramPresenter(markdown_converter=mock_markdown)

def test_presenter_uses_markdown_converter(presenter, mock_markdown):
    # Configuramos el mock para devolver un HTML conocido
    mock_markdown.to_html.return_value = "<b>hello</b>"
    
    resp = AIResponse(text="**hello**", success=True)
    formatted = presenter.format_response(resp)
    
    # Verificamos que se llamó al convertidor
    mock_markdown.to_html.assert_called_once_with("**hello**")
    assert "<b>hello</b>" in formatted[0]

def test_presenter_sanitizes_unsupported_tags(presenter, mock_markdown):
    # Simulamos que el convertidor devuelve etiquetas no soportadas
    mock_markdown.to_html.return_value = "<h1>Titulo</h1><div>Content</div>"
    
    resp = AIResponse(text="any", success=True)
    formatted = presenter.format_response(resp)
    
    # Verificamos la sanitización
    assert "<b>Titulo</b>" in formatted[0]
    assert "<h1>" not in formatted[0]
    assert "<div>" not in formatted[0]

def test_presenter_formats_error_response(presenter):
    resp = AIResponse(text="", success=False, error_message="Error <critico>")
    formatted = presenter.format_response(resp)
    
    assert "<b>Error de IA</b>" in formatted[0]
    assert "&lt;critico&gt;" in formatted[0]
