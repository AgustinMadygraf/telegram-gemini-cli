import pytest
from unittest.mock import AsyncMock, MagicMock
from src.interface_adapters.controllers.telegram_controller import TelegramController

@pytest.fixture
def mock_use_case():
    return AsyncMock()

@pytest.fixture
def controller(mock_use_case):
    return TelegramController(
        use_case=mock_use_case,
        secret_token="secret_token"
    )

@pytest.mark.asyncio
async def test_process_webhook_invalid_token(controller):
    with pytest.raises(PermissionError):
        await controller.process_webhook_data({}, "wrong_token")

@pytest.mark.asyncio
async def test_process_webhook_no_message(controller):
    # Update sin campo 'message'
    data = {"update_id": 1, "edited_message": {}}
    result = await controller.process_webhook_data(data, "secret_token")
    assert result is None

@pytest.mark.asyncio
async def test_process_webhook_valid_message(controller):
    data = {
        "update_id": 1,
        "message": {
            "chat": {"id": 123},
            "from": {"id": 456, "username": "agustin"},
            "text": "hola"
        }
    }
    msg = await controller.process_webhook_data(data, "secret_token")
    assert msg.chat_id == 123
    assert msg.text == "hola"

@pytest.mark.asyncio
async def test_execute_task(controller, mock_use_case):
    msg = MagicMock()
    await controller.execute_task(msg)
    mock_use_case.execute.assert_called_once_with(msg)
