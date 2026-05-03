"""
Path: tests/test_process_message_use_case.py
"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from src.use_cases.process_message import ProcessMessageUseCase
from src.entities.chat import ChatMessage
from src.entities.ai import AIResponse
from src.use_cases.services.resilience_service import CircuitBreakerService, CircuitState

@pytest.fixture
def mock_ai():
    return AsyncMock()

@pytest.fixture
def mock_messenger():
    return AsyncMock()

@pytest.fixture
def mock_file_gateway():
    return AsyncMock()

@pytest.fixture
def mock_presenter():
    mock = MagicMock()
    mock.format_response.return_value = ["formatted message"]
    return mock

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def mock_history():
    return AsyncMock()

@pytest.fixture
def circuit_breaker():
    return CircuitBreakerService(failure_threshold=2, recovery_timeout=1)

@pytest.mark.asyncio
async def test_execute_success(mock_ai, mock_messenger, mock_presenter, mock_logger, mock_history):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai, messenger=mock_messenger, presenter=mock_presenter,
        logger=mock_logger, allowed_users=[123], history=mock_history
    )
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    mock_ai.ask.return_value = AIResponse(text="respuesta", success=True)
    await use_case.execute(msg)
    mock_messenger.set_typing.assert_called_once_with(456)
    mock_ai.ask.assert_called_once()
    mock_history.save_message.assert_called()

@pytest.mark.asyncio
async def test_execute_with_attachments(mock_ai, mock_messenger, mock_file_gateway, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai, messenger=mock_messenger, file_gateway=mock_file_gateway,
        presenter=mock_presenter, logger=mock_logger, allowed_users=[123]
    )
    msg = ChatMessage(chat_id=456, user_id=123, text="foto", photo_ids=["p1"])
    mock_file_gateway.get_file_path.return_value = "remote/p1"
    mock_file_gateway.download_file.return_value = True
    mock_ai.ask.return_value = AIResponse(text="ok", success=True)
    with patch("os.path.exists", return_value=True), patch("os.remove") as mock_remove:
        await use_case.execute(msg)
        mock_file_gateway.download_file.assert_called_once()
        mock_remove.assert_called_once()

@pytest.mark.asyncio
async def test_execute_unauthorized(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[999])
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    with pytest.raises(PermissionError):
        await use_case.execute(msg)

@pytest.mark.asyncio
async def test_execute_reset_command(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[123])
    msg = ChatMessage(chat_id=456, user_id=123, text="/reset")
    mock_ai.reset.return_value = True
    await use_case.execute(msg)
    mock_ai.reset.assert_called_once()
    assert "reiniciado" in mock_messenger.send_message.call_args.kwargs["text"].lower()

@pytest.mark.asyncio
async def test_circuit_breaker_activation(mock_ai, mock_messenger, mock_presenter, mock_logger, circuit_breaker):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai, messenger=mock_messenger, presenter=mock_presenter,
        logger=mock_logger, allowed_users=[123], circuit_breaker=circuit_breaker
    )
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    mock_ai.ask.return_value = AIResponse(text="", success=False, error_message="fail")
    await use_case.execute(msg)
    await use_case.execute(msg)
    assert circuit_breaker.state == CircuitState.OPEN
    mock_ai.ask.reset_mock()
    await use_case.execute(msg)
    mock_ai.ask.assert_not_called()

@pytest.mark.asyncio
async def test_execute_ai_failure_ui_fallback(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[123])
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    mock_ai.ask.return_value = AIResponse(text="", success=False, error_message="fatal")
    
    # Hacer que el presenter devuelva el texto que recibe para validar el fallback
    mock_presenter.format_response.side_effect = lambda resp: [resp.text]
    
    await use_case.execute(msg)
    # Debe enviar el mensaje de error técnico amigable
    assert "Error Técnico" in mock_messenger.send_message.call_args.kwargs["text"]
