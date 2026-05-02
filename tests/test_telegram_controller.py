import pytest
from unittest.mock import AsyncMock
from src.interface_adapters.controllers.telegram_controller import TelegramController

@pytest.fixture
def mock_use_case():
    return AsyncMock()

@pytest.fixture
def controller(mock_use_case):
    return TelegramController(use_case=mock_use_case, secret_token="secure_token")

@pytest.mark.asyncio
async def test_process_webhook_valid_token(controller, mock_use_case):
    data = {
        "message": {
            "chat": {"id": 123},
            "from": {"id": 456, "username": "agustin"},
            "text": "hola"
        }
    }
    
    msg = await controller.process_webhook_data(data, x_token="secure_token")
    
    assert msg.chat_id == 123
    assert msg.user_id == 456
    assert msg.text == "hola"
    mock_use_case.validate_user.assert_called_once_with(456, 123)

@pytest.mark.asyncio
async def test_process_webhook_invalid_token(controller):
    data = {"message": {"text": "hola"}}
    with pytest.raises(PermissionError, match="Invalid secret token"):
        await controller.process_webhook_data(data, x_token="wrong_token")

@pytest.mark.asyncio
async def test_execute_task(controller, mock_use_case):
    from src.entities.chat import ChatMessage
    msg = ChatMessage(chat_id=123, user_id=456, text="hola")
    await controller.execute_task(msg)
    mock_use_case.execute.assert_called_once_with(msg)
