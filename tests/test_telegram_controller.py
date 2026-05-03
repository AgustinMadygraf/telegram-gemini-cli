"""
Path: tests/test_telegram_controller.py
"""
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
        secret_token="secret"
    )

@pytest.mark.asyncio
async def test_handle_webhook_invalid_token(controller):
    with pytest.raises(PermissionError):
        await controller.handle_webhook({}, "wrong")

@pytest.mark.asyncio
async def test_handle_webhook_valid(controller):
    data = {
        "message": {
            "chat": {"id": 123},
            "from": {"id": 456},
            "text": "hola"
        }
    }
    msg, trace_id = await controller.handle_webhook(data, "secret")
    assert msg.chat_id == 123
    assert trace_id.startswith("TR-")

@pytest.mark.asyncio
async def test_execute_task_with_trace(controller, mock_use_case):
    msg = MagicMock()
    await controller.execute_task(msg, "TR-TEST")
    mock_use_case.execute.assert_called_once_with(msg)
    # También podrías verificar que el ContextVar se seteó, pero requiere importar correlation_id
