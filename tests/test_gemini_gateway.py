import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.use_cases.ports.interfaces import ShellGateway, FileSystemGateway, GeminiConfigGateway
from src.use_cases.services.output_sanitizer import OutputSanitizerService
from src.use_cases.services.credential_manager import CredentialSyncService

@pytest.fixture
def mock_shell():
    return AsyncMock(spec=ShellGateway)

@pytest.fixture
def mock_fs():
    mock = MagicMock(spec=FileSystemGateway)
    mock.exists.return_value = True
    mock.get_absolute_path.side_effect = lambda x: f"/abs/{x}"
    return mock

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def mock_sanitizer():
    return OutputSanitizerService()

@pytest.fixture
def mock_credential_service():
    return MagicMock(spec=CredentialSyncService)

@pytest.fixture
def mock_config_gateway():
    mock = MagicMock(spec=GeminiConfigGateway)
    mock.get_include_directories.return_value = ["/mcp/path"]
    return mock

@pytest.fixture
def adapter(mock_shell, mock_fs, mock_logger, mock_sanitizer, mock_credential_service, mock_config_gateway):
    return GeminiCLIAdapter(
        shell=mock_shell,
        fs=mock_fs,
        logger=mock_logger,
        sanitizer=mock_sanitizer,
        credential_service=mock_credential_service,
        config_gateway=mock_config_gateway,
        api_key="fake-key"
    )

@pytest.mark.asyncio
async def test_validate_binary_not_found(mock_shell, mock_fs, mock_logger, mock_sanitizer, mock_credential_service, mock_config_gateway):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer, mock_credential_service, mock_config_gateway, binary_path="/wrong/path")
    mock_fs.exists.return_value = False
    assert await adapter.validate() is False

@pytest.mark.asyncio
async def test_ask_unexpected_exception(adapter, mock_shell):
    mock_shell.execute.side_effect = RuntimeError("Panic")
    resp = await adapter.ask("prompt")
    assert resp.success is False
    assert "Panic" in resp.error_message

@pytest.mark.asyncio
async def test_reset_success(adapter, mock_fs):
    assert await adapter.reset("user1") is True
    mock_fs.remove_directory.assert_called()

def test_google_auth_inheritance_calls_service(mock_shell, mock_fs, mock_logger, mock_sanitizer, mock_credential_service, mock_config_gateway):
    """Verifica que el adaptador delegue la sincronización al servicio."""
    adapter = GeminiCLIAdapter(
        mock_shell, mock_fs, mock_logger, mock_sanitizer, 
        mock_credential_service, mock_config_gateway,
        auth_method="google_auth"
    )
    adapter._get_env_for_session("user1")
    mock_credential_service.sync_credentials.assert_called()

@pytest.mark.asyncio
async def test_ask_uses_config_gateway(adapter, mock_shell, mock_config_gateway):
    mock_shell.execute.return_value = (0, "ok", "")
    await adapter.ask("test prompt")
    mock_config_gateway.get_include_directories.assert_called()
    
    args, kwargs = mock_shell.execute.call_args
    cli_args = args[0]
    assert "--include-directories" in cli_args
    assert "/mcp/path" in cli_args

@pytest.mark.asyncio
async def test_validate_success(mock_shell, mock_fs, mock_logger, mock_sanitizer, mock_credential_service, mock_config_gateway):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer, mock_credential_service, mock_config_gateway)
    mock_shell.execute.side_effect = [
        (0, "/usr/bin/rg", ""),
        (0, "hi", "")
    ]
    assert await adapter.validate() is True
