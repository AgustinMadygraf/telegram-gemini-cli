import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from src.interface_adapters.gateways.gemini_gateway import GeminiCLIAdapter

@pytest.fixture
def mock_shell():
    return AsyncMock()

@pytest.fixture
def mock_fs():
    mock = MagicMock()
    mock.exists.return_value = True
    return mock

@pytest.fixture
def adapter(mock_shell, mock_fs):
    return GeminiCLIAdapter(
        shell=mock_shell,
        fs=mock_fs,
        binary_path="/bin/gemini",
        auth_method="api_key",
        api_key="sk-123"
    )

@pytest.mark.asyncio
async def test_validate_success(adapter, mock_shell):
    mock_shell.execute.return_value = (0, "version 1.0", "")
    assert await adapter.validate() is True

@pytest.mark.asyncio
async def test_ask_success(adapter, mock_shell):
    mock_shell.execute.return_value = (0, "respuesta de la ia", "")
    
    resp = await adapter.ask("pregunta", session_id="user1")
    
    assert resp.success is True
    assert resp.text == "respuesta de la ia"
    # Verificar que se usó el entorno correcto
    args, kwargs = mock_shell.execute.call_args
    assert "GEMINI_CLI_HOME" in kwargs["env"]
    assert "user1" in kwargs["env"]["GEMINI_CLI_HOME"]
    assert kwargs["env"]["GEMINI_API_KEY"] == "sk-123"

@pytest.mark.asyncio
async def test_ask_retry_without_resume(adapter, mock_shell):
    # Primera llamada falla por falta de sesión
    # Segunda llamada (reintento) tiene éxito
    mock_shell.execute.side_effect = [
        (1, "", "Error: no session found"),
        (0, "respuesta sin resume", "")
    ]
    
    resp = await adapter.ask("pregunta", session_id="new_user")
    
    assert resp.success is True
    assert resp.text == "respuesta sin resume"
    assert mock_shell.execute.call_count == 2
    # Verificar que el segundo comando NO tenía --resume
    second_call_args = mock_shell.execute.call_args_list[1][0][0]
    assert "--resume" not in second_call_args

@pytest.mark.asyncio
async def test_reset(adapter, mock_shell):
    await adapter.reset("user1")
    mock_shell.execute.assert_called_once()
    assert "rm" in mock_shell.execute.call_args[0][0]
    assert "user1" in mock_shell.execute.call_args[0][0][-1]

def test_google_auth_inheritance(mock_shell, mock_fs):
    adapter = GeminiCLIAdapter(
        shell=mock_shell,
        fs=mock_fs,
        auth_method="google_auth"
    )
    
    mock_fs.exists.side_effect = [True, False] # Existe global, no existe local
    
    with patch("shutil.copytree") as mock_copy:
        env = adapter._get_env_for_session("user1")
        assert mock_copy.called
        assert "GEMINI_CLI_HOME" in env

def test_vertex_ai_strategy(mock_shell, mock_fs):
    adapter = GeminiCLIAdapter(
        shell=mock_shell,
        fs=mock_fs,
        auth_method="vertex_ai",
        vertex_project="p1",
        vertex_location="l1"
    )
    env = adapter._get_env_for_session("user1")
    assert env["GOOGLE_GENAI_USE_VERTEXAI"] == "true"
    assert env["GOOGLE_CLOUD_PROJECT"] == "p1"
    assert env["GOOGLE_CLOUD_LOCATION"] == "l1"

@pytest.mark.asyncio
async def test_ask_failure_system_error(adapter, mock_shell):
    # Simulamos un error de ejecución (ej: falta de memoria o crash)
    mock_shell.execute.return_value = (127, "", "Binary not found or crash")
    
    resp = await adapter.ask("pregunta", session_id="user1")
    
    assert resp.success is False
    assert "crash" in resp.error_message.lower()
