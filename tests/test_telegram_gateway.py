import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.interface_adapters.gateways.telegram_gateway import TelegramAdapter
from telegram.error import TelegramError
from src.use_cases.ports.interfaces import LoggerPort

@pytest.fixture
def mock_logger():
    return MagicMock(spec=LoggerPort)

@pytest.fixture
def mock_bot():
    with patch("src.interface_adapters.gateways.telegram_gateway.Bot") as mock:
        bot_instance = MagicMock()
        bot_instance.get_me = AsyncMock()
        bot_instance.send_message = AsyncMock()
        bot_instance.send_chat_action = AsyncMock()
        bot_instance.get_webhook_info = AsyncMock()
        bot_instance.set_webhook = AsyncMock()
        mock.return_value = bot_instance
        yield bot_instance

@pytest.mark.asyncio
async def test_validate_exception(mock_bot, mock_logger):
    adapter = TelegramAdapter(token="fake:token", logger=mock_logger)
    mock_bot.get_me.side_effect = RuntimeError("API Down")
    assert await adapter.validate() is False
    mock_logger.error.assert_called()

@pytest.mark.asyncio
async def test_set_typing_exception(mock_bot, mock_logger):
    adapter = TelegramAdapter(token="fake:token", logger=mock_logger)
    mock_bot.send_chat_action.side_effect = Exception("Silent fail")
    await adapter.set_typing(123) 

@pytest.mark.asyncio
async def test_send_message_payload_logging(mock_bot, mock_logger):
    adapter = TelegramAdapter(token="fake:token", logger=mock_logger)
    # Simulamos error 400 de Telegram
    mock_bot.send_message.side_effect = TelegramError("Bad Request")
    
    await adapter.send_message(123, "malformed <b>text", parse_mode="HTML")
    
    # Verificamos que se logueó el error Y el payload
    assert mock_logger.error.call_count >= 2
    args_list = [call.args[0] for call in mock_logger.error.call_args_list]
    assert any("Payload fallido" in arg for arg in args_list)
    assert any("malformed <b>text" in arg for arg in args_list)

@pytest.mark.asyncio
async def test_get_webhook_status(mock_bot, mock_logger):
    adapter = TelegramAdapter(token="fake:token", logger=mock_logger)
    mock_info = MagicMock()
    mock_info.url = "http://test.com"
    mock_bot.get_webhook_info.return_value = mock_info
    state = await adapter.get_webhook_status()
    assert state.url == "http://test.com"
