import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.system_validator import SystemValidatorService

@pytest.fixture
def mock_tunnel():
    return AsyncMock()

@pytest.fixture
def mock_ai():
    # Mockeamos que sea un validador de credenciales
    mock = AsyncMock()
    mock.validate.return_value = True
    return mock

@pytest.fixture
def mock_messenger():
    return AsyncMock()

@pytest.fixture
def validator(mock_tunnel, mock_ai, mock_messenger):
    return SystemValidatorService(
        validators=[mock_ai],
        messenger=mock_messenger,
        tunnel=mock_tunnel,
        webhook_url="https://test.com",
        secret_token="secret"
    )

@pytest.mark.asyncio
async def test_validate_all_success(validator, mock_tunnel, mock_ai, mock_messenger):
    mock_tunnel.validate_tunnel.return_value = True
    mock_messenger.get_webhook_status.return_value = MagicMock(url="https://test.com", last_error_message=None)
    
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
async def test_network_validation_exception(validator, mock_messenger):
    mock_messenger.get_webhook_status.side_effect = Exception("Connection Lost")
    report = await validator.validate_all()
    assert report.is_ok is False
    assert any("Fallo de conexión" in msg for msg in report.error_messages)
