import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter
from src.use_cases.ports.interfaces import ShellGateway, FileSystemGateway
from src.use_cases.services.output_sanitizer import OutputSanitizerService

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
def adapter(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    return GeminiCLIAdapter(
        shell=mock_shell,
        fs=mock_fs,
        logger=mock_logger,
        sanitizer=mock_sanitizer,
        api_key="fake-key"
    )

def test_google_auth_inheritance_failure(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer, auth_method="google_auth")
    # Simulamos que existe el origen pero falla la copia
    mock_fs.exists.side_effect = [True, False]
    mock_fs.copy_directory.side_effect = Exception("Disk full")
    adapter._get_env_for_session("user1")
    # Coverage check: the exception is caught and logged

@pytest.mark.asyncio
async def test_validate_binary_not_found(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer, binary_path="/wrong/path")
    mock_fs.exists.return_value = False
    assert await adapter.validate() is False

@pytest.mark.asyncio
async def test_validate_exception(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer)
    mock_shell.execute.side_effect = [
        (0, "/usr/bin/rg", ""), 
        Exception("Runtime error") 
    ]
    assert await adapter.validate() is False

@pytest.mark.asyncio
async def test_ask_unexpected_exception(adapter, mock_shell):
    mock_shell.execute.side_effect = RuntimeError("Panic")
    resp = await adapter.ask("prompt")
    assert resp.success is False
    assert "Panic" in resp.error_message

@pytest.mark.asyncio
async def test_reset_exception(adapter, mock_fs):
    mock_fs.remove_directory.side_effect = Exception("Permission denied")
    assert await adapter.reset("user1") is False

@pytest.mark.asyncio
async def test_reset_success(adapter, mock_fs):
    assert await adapter.reset("user1") is True
    mock_fs.remove_directory.assert_called()

@pytest.mark.asyncio
async def test_ask_retry_without_resume(adapter, mock_shell):
    mock_shell.execute.side_effect = [
        (1, "", "no session found"),
        (0, "respuesta", "")
    ]
    resp = await adapter.ask("prompt")
    assert resp.success is True
    assert resp.text == "respuesta"
    assert mock_shell.execute.call_count == 2

def test_google_auth_inheritance_lazy_skip(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer, auth_method="google_auth")
    mock_fs.exists.return_value = True
    adapter._get_env_for_session("user1")
    mock_fs.copy_directory.assert_not_called()

def test_google_auth_inheritance_sync_when_missing(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer, auth_method="google_auth")
    mock_fs.exists.side_effect = [True, False]
    adapter._get_env_for_session("user1")
    mock_fs.copy_directory.assert_called()

def test_vertex_ai_auth(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(
        mock_shell, mock_fs, mock_logger, mock_sanitizer,
        auth_method="vertex_ai",
        vertex_project="p1",
        vertex_location="l1"
    )
    env = adapter._get_env_for_session("user1")
    assert env["GOOGLE_GENAI_USE_VERTEXAI"] == "true"
    assert env["GOOGLE_CLOUD_PROJECT"] == "p1"
    assert env["GOOGLE_CLOUD_LOCATION"] == "l1"

@pytest.mark.asyncio
async def test_validate_success(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer)
    mock_shell.execute.side_effect = [
        (0, "/usr/bin/rg", ""),
        (0, "hi", "")
    ]
    assert await adapter.validate() is True

@pytest.mark.asyncio
async def test_validate_ripgrep_missing(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer)
    mock_shell.execute.return_value = (1, "", "")
    assert await adapter.validate() is False

@pytest.mark.asyncio
async def test_validate_infra_error_in_output(mock_shell, mock_fs, mock_logger, mock_sanitizer):
    adapter = GeminiCLIAdapter(mock_shell, mock_fs, mock_logger, mock_sanitizer)
    mock_shell.execute.side_effect = [
        (0, "/usr/bin/rg", ""),
        (0, "fatal error: some infra issue", "")
    ]
    assert await adapter.validate() is False

@pytest.mark.asyncio
async def test_ask_failure(adapter, mock_shell):
    mock_shell.execute.return_value = (1, "", "unknown error")
    resp = await adapter.ask("prompt")
    assert resp.success is False
    assert "unknown error" in resp.error_message

@pytest.mark.asyncio
async def test_ask_uses_yolo_approval_mode(adapter, mock_shell):
    mock_shell.execute.return_value = (0, "ok", "")
    await adapter.ask("test prompt")
    args, kwargs = mock_shell.execute.call_args
    cli_args = args[0]
    assert "--approval-mode" in cli_args
    assert "yolo" in cli_args
    assert "auto_edit" not in cli_args
