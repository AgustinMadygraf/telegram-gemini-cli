import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.process_message import ProcessMessageUseCase
from src.entities.chat import ChatMessage
from src.entities.ai import AIResponse

@pytest.fixture
def mock_ai():
    return AsyncMock()

@pytest.fixture
def mock_messenger():
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

@pytest.mark.asyncio
async def test_execute_success(mock_ai, mock_messenger, mock_presenter, mock_logger, mock_history):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai,
        messenger=mock_messenger,
        presenter=mock_presenter,
        logger=mock_logger,
        allowed_users=[123],
        history=mock_history
    )
    
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    mock_ai.ask.return_value = AIResponse(text="respuesta", success=True)
    
    await use_case.execute(msg)
    
    mock_messenger.set_typing.assert_called_once_with(456)
    mock_ai.ask.assert_called_once_with("hola", session_id="chat_456", attachments=[])
    mock_history.save_message.assert_called()
    assert mock_history.save_message.call_count == 2 # User msg + AI msg
    
    mock_messenger.send_message.assert_called_with(
        chat_id=456, 
        text="formatted message",
        parse_mode="HTML"
    )

@pytest.mark.asyncio
async def test_execute_with_attachments(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai,
        messenger=mock_messenger,
        presenter=mock_presenter,
        logger=mock_logger,
        allowed_users=[123]
    )
    
    msg = ChatMessage(chat_id=456, user_id=123, text="mira esto", photo_ids=["p1", "p2"])
    mock_messenger.get_file_path.side_effect = ["remote/p1", "remote/p2"]
    mock_messenger.download_file.return_value = True
    mock_ai.ask.return_value = AIResponse(text="veo dos fotos", success=True)
    
    with patch("os.path.exists", return_value=True), \
         patch("os.remove") as mock_remove:
        await use_case.execute(msg)
        
        assert mock_messenger.download_file.call_count == 2
        assert len(mock_ai.ask.call_args.kwargs["attachments"]) == 2
        assert mock_remove.call_count == 2

@pytest.mark.asyncio
async def test_execute_attachment_download_failure(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[123])
    msg = ChatMessage(chat_id=456, user_id=123, text="foto", photo_ids=["p1"])
    mock_messenger.get_file_path.return_value = "remote/p1"
    mock_messenger.download_file.return_value = False
    mock_ai.ask.return_value = AIResponse(text="no veo nada", success=True)
    
    await use_case.execute(msg)
    assert len(mock_ai.ask.call_args.kwargs["attachments"]) == 0

@pytest.mark.asyncio
async def test_execute_attachment_cleanup_failure(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[123])
    msg = ChatMessage(chat_id=456, user_id=123, text="foto", photo_ids=["p1"])
    mock_messenger.get_file_path.return_value = "remote/p1"
    mock_messenger.download_file.return_value = True
    mock_ai.ask.return_value = AIResponse(text="ok", success=True)
    
    with patch("os.path.exists", return_value=True), \
         patch("os.remove", side_effect=Exception("Locked")):
        await use_case.execute(msg)
        mock_logger.warning.assert_called()

@pytest.mark.asyncio
async def test_execute_unauthorized(mock_ai, mock_messenger, mock_presenter):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai,
        messenger=mock_messenger,
        presenter=mock_presenter,
        logger=mock_logger,
        allowed_users=[999]
    )
    
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    
    with pytest.raises(PermissionError):
        await use_case.execute(msg)
    
    mock_ai.ask.assert_not_called()
    mock_messenger.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_execute_reset_command(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai,
        messenger=mock_messenger,
        presenter=mock_presenter,
        logger=mock_logger,
        allowed_users=[123]
    )
    
    msg = ChatMessage(chat_id=456, user_id=123, text="/reset")
    mock_ai.reset.return_value = True
    
    await use_case.execute(msg)
    
    mock_ai.reset.assert_called_once_with(session_id="chat_456")
    assert "reiniciado" in mock_messenger.send_message.call_args.kwargs["text"].lower()

@pytest.mark.asyncio
async def test_validate_user_allowed(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[123])
    await use_case.validate_user(user_id=123, chat_id=456)
@pytest.mark.asyncio
async def test_validate_user_denied(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[999])
    with pytest.raises(PermissionError):
        await use_case.validate_user(user_id=123, chat_id=456)

@pytest.mark.asyncio
async def test_execute_reset_failure(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[123])
    msg = ChatMessage(chat_id=456, user_id=123, text="/reset")
    mock_ai.reset.return_value = False
    await use_case.execute(msg)
    assert "no se pudo reiniciar" in mock_messenger.send_message.call_args.kwargs["text"].lower()

@pytest.mark.asyncio
async def test_execute_ai_failure_logging(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[123])
    msg = ChatMessage(chat_id=456, user_id=123, text="long text " * 10)
    mock_ai.ask.return_value = AIResponse(text="", success=False, error_message="fatal error")
    await use_case.execute(msg)
    # El presenter debería formatear el error y el messenger enviarlo
    mock_presenter.format_response.assert_called_once()

@pytest.mark.asyncio
async def test_execute_log_truncation(mock_ai, mock_messenger, mock_presenter, mock_logger):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, mock_logger, allowed_users=[123])
    long_input = "word " * 20 # 100 chars
    msg = ChatMessage(chat_id=456, user_id=123, text=long_input)
    
    long_output = "answer " * 20
    mock_ai.ask.return_value = AIResponse(text=long_output, success=True)
    
    await use_case.execute(msg)
    # Solo verificamos que no crashee al imprimir logs truncados
