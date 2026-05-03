import pytest
from unittest.mock import MagicMock, patch
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.entities.ai import AIResponse
from src.use_cases.ports.interfaces import MarkdownConverterPort, LoggerPort

@pytest.fixture
def mock_markdown():
    return MagicMock(spec=MarkdownConverterPort)

@pytest.fixture
def mock_logger():
    return MagicMock(spec=LoggerPort)

@pytest.fixture
def presenter(mock_markdown, mock_logger):
    return TelegramPresenter(markdown_converter=mock_markdown, logger=mock_logger)

def test_presenter_uses_markdown_converter(presenter, mock_markdown):
    mock_markdown.to_html.return_value = "<b>hello</b>"
    resp = AIResponse(text="**hello**", success=True)
    formatted = presenter.format_response(resp)
    mock_markdown.to_html.assert_called_once_with("**hello**")
    assert "<b>hello</b>" in formatted[0]

def test_presenter_sanitizes_unsupported_tags(presenter, mock_markdown):
    mock_markdown.to_html.return_value = "<h1>Titulo</h1><div>Content</div>"
    resp = AIResponse(text="any", success=True)
    formatted = presenter.format_response(resp)
    assert "<b>Titulo</b>" in formatted[0]
    assert "<h1>" not in formatted[0]
    assert "<div>" not in formatted[0]

def test_presenter_formats_error_response(presenter):
    resp = AIResponse(text="", success=False, error_message="Error <critico>")
    formatted = presenter.format_response(resp)
    assert "<b>Error de IA</b>" in formatted[0]
    assert "&lt;critico&gt;" in formatted[0]

def test_presenter_converts_lists_and_cleans_code(presenter, mock_markdown):
    mock_markdown.to_html.return_value = '<ul><li>Item 1</li></ul><pre><code class="language-py">print()</code></pre>'
    resp = AIResponse(text="any", success=True)
    formatted = presenter.format_response(resp)
    assert "• Item 1" in formatted[0]
    assert "<ul>" not in formatted[0]
    assert '<code class="language-py">' not in formatted[0]
    assert '<code>' in formatted[0]

def test_presenter_replaces_br_with_newline(presenter, mock_markdown):
    mock_markdown.to_html.return_value = 'Texto<br>con<br />saltos'
    resp = AIResponse(text="any", success=True)
    formatted = presenter.format_response(resp)
    assert "Texto\ncon\nsaltos" in formatted[0]
    assert "<br" not in formatted[0]

def test_presenter_handles_large_error(presenter, mock_logger):
    massive_error = "x" * 1500
    resp = AIResponse(text="", success=False, error_message=massive_error)
    formatted = presenter.format_response(resp)
    assert len(formatted) > 1
    assert "Fallo técnico en Gemini" in formatted[0]
    mock_logger.warning.assert_called()

def test_presenter_handles_markdown_exception(presenter, mock_markdown, mock_logger):
    mock_markdown.to_html.side_effect = Exception("Crash")
    resp = AIResponse(text="<b>fallback</b>", success=True)
    formatted = presenter.format_response(resp)
    assert "&lt;b&gt;fallback&lt;/b&gt;" in formatted[0]
    mock_logger.error.assert_called()

def test_presenter_chunks_long_response(presenter, mock_markdown):
    long_text = ("line\n" * 500) # 2500 chars approx
    mock_markdown.to_html.return_value = long_text
    resp = AIResponse(text="any", success=True)
    
    # Reducimos el límite para forzar chunking en el test
    with patch.object(presenter, '_chunk_text', side_effect=presenter._chunk_text) as mock_chunk:
        formatted = presenter.format_response(resp)
    
    # El limit por defecto es 4000, 2500 no debería fragmentarse.
    # Vamos a probar con algo realmente largo.
    very_long_text = "word " * 1000 # 5000 chars
    mock_markdown.to_html.return_value = very_long_text
    formatted = presenter.format_response(resp)
    assert len(formatted) >= 2

def test_presenter_cleans_excessive_newlines(presenter, mock_markdown):
    mock_markdown.to_html.return_value = "Line 1\n\n\n\nLine 2"
    resp = AIResponse(text="any", success=True)
    formatted = presenter.format_response(resp)
    assert "Line 1\n\nLine 2" in formatted[0]
    assert "\n\n\n" not in formatted[0]

def test_chunk_text_no_newline_split(presenter):
    # Caso donde no hay saltos de línea para cortar
    long_word = "a" * 100
    chunks = presenter._chunk_text(long_word, limit=10)
    assert len(chunks) == 10
    assert all(len(c) == 10 for c in chunks)
