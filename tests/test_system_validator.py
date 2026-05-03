"""
Path: tests/test_system_validator.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.system_validator import SystemValidatorService
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.entities.network import WebhookStatus

@pytest.fixture
def mock_tunnel():
    return AsyncMock()

@pytest.fixture
def mock_ai():
    mock = MagicMock(spec=GeminiCLIAdapter)
    mock.validate = AsyncMock(return_value=True)
    mock.auth_method = "api_key"
    return mock

@pytest.fixture
def mock_messenger():
    return AsyncMock()

@pytest.fixture
def mock_web_admin():
    mock = AsyncMock()
    mock.get_webhook_status.return_value = WebhookStatus(
        url="https://test.com",
        has_custom_certificate=False,
        pending_update_count=0,
        last_error_date=None,
        last_error_message=None,
        max_connections=40,
        ip_address=None
    )
    return mock

@pytest.fixture
def mock_mcp():
    mock = AsyncMock()
    mock.validate_servers.return_value = [("test", True, "")]
    return mock

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def validator(mock_tunnel, mock_ai, mock_messenger, mock_web_admin, mock_mcp, mock_logger):
    return SystemValidatorService(
        validators=[mock_ai],
        logger=mock_logger,
        messenger=mock_messenger,
        web_admin=mock_web_admin,
        tunnel=mock_tunnel,
        mcp_validator=mock_mcp,
        webhook_url="https://test.com",
        secret_token="secret"
    )

@pytest.mark.asyncio
async def test_validate_all_success(validator, mock_tunnel, mock_web_admin):
    mock_tunnel.validate_tunnel.return_value = True
    report = await validator.validate_all()
    assert report.is_ok is True
    assert "Sistema validado correctamente" in report.info_messages[-1]

@pytest.mark.asyncio
async def test_validate_ai_failure(validator, mock_ai):
    mock_ai.validate.return_value = False
    report = await validator.validate_all()
    assert report.is_ok is False
    assert any("Fallo en validador" in msg for msg in report.error_messages)

@pytest.mark.asyncio
async def test_validate_tunnel_degraded(validator, mock_tunnel):
    mock_tunnel.validate_tunnel.return_value = False
    report = await validator.validate_all()
    assert report.is_ok is True 
    assert any("Túnel no detectado" in msg for msg in report.info_messages)

@pytest.mark.asyncio
async def test_network_validation_exception(validator, mock_web_admin):
    mock_web_admin.get_webhook_status.side_effect = Exception("Connection Lost")
    report = await validator.validate_all()
    assert report.is_ok is False
    assert any("Fallo de conexión" in msg for msg in report.error_messages)

@pytest.mark.asyncio
async def test_mcp_validation_failure(validator, mock_mcp):
    mock_mcp.validate_servers.return_value = [("xubio", False, "Missing build")]
    report = await validator.validate_all()
    assert report.is_ok is False
    assert any("MCP 'xubio': NO DISPONIBLE" in msg for msg in report.error_messages)

@pytest.mark.asyncio
async def test_validate_network_out_of_sync(validator, mock_web_admin):
    mock_web_admin.get_webhook_status.return_value = WebhookStatus(
        url="https://different.com", has_custom_certificate=False, pending_update_count=0,
        last_error_date=None, last_error_message=None, max_connections=40, ip_address=None
    )
    await validator.validate_all()
    mock_web_admin.set_webhook.assert_called_once()

@pytest.mark.asyncio
async def test_validate_network_sync_failure(validator, mock_web_admin):
    mock_web_admin.get_webhook_status.return_value = WebhookStatus(
        url="", has_custom_certificate=False, pending_update_count=0,
        last_error_date=None, last_error_message=None, max_connections=40, ip_address=None
    )
    mock_web_admin.set_webhook.side_effect = Exception("Forbidden")
    report = await validator.validate_all()
    assert any("Telegram rechazó el Webhook: Forbidden" in msg for msg in report.error_messages)
