import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.system_validator import SystemValidatorService
from src.entities.validation import ValidationReport

@pytest.mark.asyncio
async def test_validator_all_ok():
    # Mock Gateways
    v1 = AsyncMock()
    v1.validate.return_value = True
    
    messenger = AsyncMock()
    messenger.get_webhook_status.return_value = MagicMock(url="http://test.com", last_error_message=None)
    
    tunnel = AsyncMock()
    tunnel.validate_tunnel.return_value = True
    
    service = SystemValidatorService(
        validators=[v1],
        messenger=messenger,
        tunnel=tunnel,
        webhook_url="http://test.com"
    )
    
    report = await service.validate_all()
    
    assert report.is_ok
    assert any("Sistema validado correctamente" in msg for msg in report.info_messages)

@pytest.mark.asyncio
async def test_validator_fails_on_credentials():
    v1 = AsyncMock()
    v1.validate.return_value = False
    
    service = SystemValidatorService(
        validators=[v1],
        webhook_url="http://test.com"
    )
    
    report = await service.validate_all()
    
    assert not report.is_ok
    assert any("Fallo en validador de credenciales" in msg for msg in report.error_messages)

@pytest.mark.asyncio
async def test_validator_syncs_webhook_if_different():
    v1 = AsyncMock()
    v1.validate.return_value = True
    
    messenger = AsyncMock()
    # URL diferente a la configurada
    messenger.get_webhook_status.return_value = MagicMock(url="http://old.com", last_error_message=None)
    
    service = SystemValidatorService(
        validators=[v1],
        messenger=messenger,
        webhook_url="http://new.com"
    )
    
    report = await service.validate_all()
    
    assert report.is_ok
    messenger.set_webhook.assert_awaited_once_with(url="http://new.com", secret_token="")
