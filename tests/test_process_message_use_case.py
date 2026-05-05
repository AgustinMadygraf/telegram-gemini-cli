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
from src.use_cases.services.attachment_manager import AttachmentManager
from src.use_cases.services.command_dispatcher import CommandDispatcher

@pytest.fixture
def mock_ai():
    return AsyncMock()

@pytest.fixture
def mock_messenger():
    return AsyncMock()

@pytest.fixture
def mock_attachment_manager():
    mock = MagicMock(spec=AttachmentManager)
    mock.download_attachments = AsyncMock(return_value=[])
    return mock

@pytest.fixture
def mock_command_dispatcher():
    mock = AsyncMock(spec=CommandDispatcher)
    mock.is_command.return_value = False
    return mock

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
async def test_execute_success(mock_ai, mock_messenger, mock_presenter, mock_logger, mock_history, mock_attachment_manager, mock_command_dispatcher):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai, messenger=mock_messenger, presenter=mock_presenter,
        logger=mock_logger, allowed_users=[123], history=mock_history,
        attachment_manager=mock_attachment_manager,
        command_dispatcher=mock_command_dispatcher
    )
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    mock_ai.ask.return_value = AIResponse(text="respuesta", success=True)
    await use_case.execute(msg)
    mock_messenger.set_typing.assert_called_once_with(456)
    # Verificar que se llamó con el historial vacío (o el historial que devuelva el mock)
    args, kwargs = mock_ai.ask.call_args
    assert args[0] == "hola"
    assert "history" in kwargs
    mock_history.save_message.assert_called()

@pytest.mark.asyncio
async def test_execute_with_attachments(mock_ai, mock_messenger, mock_attachment_manager, mock_command_dispatcher, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai, messenger=mock_messenger,
        presenter=mock_presenter, logger=mock_logger, allowed_users=[123],
        attachment_manager=mock_attachment_manager,
        command_dispatcher=mock_command_dispatcher
    )
    msg = ChatMessage(chat_id=456, user_id=123, text="foto", photo_ids=["p1"])
    mock_attachment_manager.download_attachments.return_value = ["local/p1"]
    mock_ai.ask.return_value = AIResponse(text="ok", success=True)
    await use_case.execute(msg)
    mock_attachment_manager.download_attachments.assert_called_once()
    mock_attachment_manager.cleanup.assert_called_once()

@pytest.mark.asyncio
async def test_execute_unauthorized(mock_ai, mock_messenger, mock_presenter, mock_logger, mock_attachment_manager, mock_command_dispatcher):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, [999], mock_attachment_manager, mock_command_dispatcher)
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    with pytest.raises(PermissionError):
        await use_case.execute(msg)

@pytest.mark.asyncio
async def test_execute_reset_command(mock_ai, mock_messenger, mock_presenter, mock_logger, mock_attachment_manager, mock_command_dispatcher):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, [123], mock_attachment_manager, mock_command_dispatcher)
    msg = ChatMessage(chat_id=456, user_id=123, text="/reset")
    # El CommandDispatcher es quien maneja esto ahora
    mock_command_dispatcher.is_command.return_value = True
    mock_command_dispatcher.dispatch.return_value = True
    await use_case.execute(msg)
    mock_command_dispatcher.dispatch.assert_called_once()

@pytest.mark.asyncio
async def test_circuit_breaker_activation(mock_ai, mock_messenger, mock_presenter, mock_logger, circuit_breaker, mock_attachment_manager, mock_command_dispatcher):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai, messenger=mock_messenger, presenter=mock_presenter,
        logger=mock_logger, allowed_users=[123], circuit_breaker=circuit_breaker,
        attachment_manager=mock_attachment_manager,
        command_dispatcher=mock_command_dispatcher
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
async def test_execute_ai_failure_ui_fallback(mock_ai, mock_messenger, mock_presenter, mock_logger, mock_attachment_manager, mock_command_dispatcher):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, [123], mock_attachment_manager, mock_command_dispatcher)
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    mock_ai.ask.return_value = AIResponse(text="", success=False, error_message="fatal")
    # Hacer que el presenter devuelva el texto que recibe para validar el fallback
    mock_presenter.format_response.side_effect = lambda resp: [resp.text]

    await use_case.execute(msg)
    # Debe enviar el mensaje de error técnico amigable (que se inyecta en el Use Case cuando falla la IA)
    args, kwargs = mock_messenger.send_message.call_args
    assert "Error Técnico" in kwargs["text"]
