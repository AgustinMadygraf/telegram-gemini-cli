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

@pytest.mark.asyncio
async def test_execute_success(mock_ai, mock_messenger, mock_presenter):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai,
        messenger=mock_messenger,
        presenter=mock_presenter,
        allowed_users=[123]
    )
    
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    mock_ai.ask.return_value = AIResponse(text="respuesta", success=True)
    
    await use_case.execute(msg)
    
    mock_messenger.set_typing.assert_called_once_with(456)
    mock_ai.ask.assert_called_once_with("hola", session_id="chat_456")
    # Verificamos que se llame a send_message con los argumentos correctos (ignorando el orden)
    mock_messenger.send_message.assert_called_with(
        chat_id=456, 
        text="formatted message",
        parse_mode="MarkdownV2"
    )

@pytest.mark.asyncio
async def test_execute_unauthorized(mock_ai, mock_messenger, mock_presenter):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai,
        messenger=mock_messenger,
        presenter=mock_presenter,
        allowed_users=[999]
    )
    
    msg = ChatMessage(chat_id=456, user_id=123, text="hola")
    
    with pytest.raises(PermissionError):
        await use_case.execute(msg)
    
    mock_ai.ask.assert_not_called()
    mock_messenger.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_execute_reset_command(mock_ai, mock_messenger, mock_presenter):
    use_case = ProcessMessageUseCase(
        ai_engine=mock_ai,
        messenger=mock_messenger,
        presenter=mock_presenter,
        allowed_users=[123]
    )
    
    msg = ChatMessage(chat_id=456, user_id=123, text="/reset")
    mock_ai.reset.return_value = True
    
    await use_case.execute(msg)
    
    mock_ai.reset.assert_called_once_with(session_id="chat_456")
    assert "reiniciado" in mock_messenger.send_message.call_args.kwargs["text"].lower()

@pytest.mark.asyncio
async def test_validate_user_allowed(mock_ai, mock_messenger, mock_presenter):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, allowed_users=[123])
    await use_case.validate_user(user_id=123, chat_id=456)

@pytest.mark.asyncio
async def test_validate_user_denied(mock_ai, mock_messenger, mock_presenter):
    use_case = ProcessMessageUseCase(mock_ai, mock_messenger, mock_presenter, allowed_users=[999])
    with pytest.raises(PermissionError):
        await use_case.validate_user(user_id=123, chat_id=456)
