import pytest
from unittest.mock import MagicMock
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
