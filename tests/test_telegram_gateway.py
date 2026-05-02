import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.interface_adapters.gateways.telegram_gateway import TelegramAdapter
from telegram.error import TelegramError

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
async def test_validate_exception(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_bot.get_me.side_effect = RuntimeError("API Down")
    assert await adapter.validate() is False # Line 20-21 coverage

@pytest.mark.asyncio
async def test_set_typing_exception(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_bot.send_chat_action.side_effect = Exception("Silent fail")
    await adapter.set_typing(123) # Line 39-40 coverage: should not raise

@pytest.mark.asyncio
async def test_set_webhook_generic_exception(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_bot.set_webhook.side_effect = ValueError("Fatal")
    result = await adapter.set_webhook("http://test.com")
    assert result is False # Line 65-66 coverage

@pytest.mark.asyncio
async def test_send_message_success(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    await adapter.send_message(123, "hola", parse_mode="MarkdownV2")
    mock_bot.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_get_webhook_status(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_info = MagicMock()
    mock_info.url = "http://test.com"
    mock_bot.get_webhook_info.return_value = mock_info
    state = await adapter.get_webhook_status()
    assert state.url == "http://test.com"
