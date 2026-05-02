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
async def test_send_message_success(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_bot.send_message.return_value = MagicMock()
    
    await adapter.send_message(123, "hola", parse_mode="MarkdownV2")
    
    mock_bot.send_message.assert_called_once_with(
        chat_id=123, 
        text="hola", 
        parse_mode="MarkdownV2"
    )

@pytest.mark.asyncio
async def test_set_typing_success(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    await adapter.set_typing(123)
    mock_bot.send_chat_action.assert_called_once_with(chat_id=123, action="typing")

@pytest.mark.asyncio
async def test_get_webhook_status(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    
    mock_info = MagicMock()
    mock_info.url = "http://test.com"
    mock_info.has_custom_certificate = False
    mock_info.pending_update_count = 0
    mock_info.last_error_date = None
    mock_info.last_error_message = None
    mock_info.max_connections = None
    mock_info.ip_address = None
    
    mock_bot.get_webhook_info.return_value = mock_info
    
    state = await adapter.get_webhook_status()
    assert state.url == "http://test.com"

@pytest.mark.asyncio
async def test_set_webhook_success(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_bot.set_webhook.return_value = True
    
    result = await adapter.set_webhook("http://test.com", "secret")
    assert result is True
    mock_bot.set_webhook.assert_called_once_with(url="http://test.com", secret_token="secret")

@pytest.mark.asyncio
async def test_validate_success(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_bot.get_me.return_value = MagicMock()
    assert await adapter.validate() is True

@pytest.mark.asyncio
async def test_set_webhook_error(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_bot.set_webhook.side_effect = TelegramError("Invalid URL")
    
    with pytest.raises(TelegramError):
        await adapter.set_webhook("http://invalid.com")

@pytest.mark.asyncio
async def test_send_message_failure(mock_bot):
    adapter = TelegramAdapter(token="fake:token")
    mock_bot.send_message.side_effect = Exception("Network error")
    
    result = await adapter.send_message(123, "hola")
    assert result is False
