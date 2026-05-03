import pytest
import json
import unittest.mock
from unittest.mock import MagicMock, patch
from src.interface_adapters.gateways.mcp_validator_adapter import MCPValidatorAdapter
from src.use_cases.ports.interfaces import FileSystemGateway

@pytest.fixture
def mock_fs():
    return MagicMock(spec=FileSystemGateway)

@pytest.mark.asyncio
async def test_validate_servers_no_config(mock_fs):
    mock_fs.exists.return_value = False
    adapter = MCPValidatorAdapter(fs=mock_fs, config_path="/fake/path.json")
    
    results = await adapter.validate_servers()
    
    assert len(results) == 1
    assert results[0][0] == "Configuración"
    assert results[0][1] is False
    assert "No se encontró" in results[0][2]

@pytest.mark.asyncio
async def test_validate_servers_invalid_json(mock_fs):
    mock_fs.exists.return_value = True
    adapter = MCPValidatorAdapter(fs=mock_fs, config_path="/fake/path.json")
    
    with patch("builtins.open", pytest.raises(Exception)):
        results = await adapter.validate_servers()
    
    assert results[0][1] is False
    assert "Error" in results[0][2]

@pytest.mark.asyncio
async def test_validate_servers_success(mock_fs):
    mock_fs.exists.return_value = True
    config_data = {
        "mcpServers": {
            "test-server": {
                "command": "node",
                "args": ["/path/to/script.js"]
            }
        }
    }
    
    adapter = MCPValidatorAdapter(fs=mock_fs, config_path="/fake/path.json")
    
    with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(config_data))):
        # El script existe
        mock_fs.exists.side_effect = [True, True] # settings.json y script.js
        results = await adapter.validate_servers()
        
    assert len(results) == 1
    assert results[0][0] == "test-server"
    assert results[0][1] is True

@pytest.mark.asyncio
async def test_validate_servers_missing_script(mock_fs):
    mock_fs.exists.return_value = True
    config_data = {
        "mcpServers": {
            "test-server": {
                "command": "node",
                "args": ["/path/to/script.js"]
            }
        }
    }
    
    adapter = MCPValidatorAdapter(fs=mock_fs, config_path="/fake/path.json")
    
    with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(config_data))):
        # El script NO existe
        mock_fs.exists.side_effect = [True, False] # settings.json existe, script.js NO
        results = await adapter.validate_servers()
        
    assert results[0][1] is False
    assert "Script no encontrado" in results[0][2]

@pytest.mark.asyncio
async def test_validate_servers_sse_detection(mock_fs):
    mock_fs.exists.return_value = True
    config_data = {
        "mcpServers": {
            "sse-server": {
                "url": "http://localhost:3000/sse"
            }
        }
    }
    
    adapter = MCPValidatorAdapter(fs=mock_fs, config_path="/fake/path.json")
    
    with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(config_data))):
        results = await adapter.validate_servers()
        
    assert results[0][0] == "sse-server"
    assert results[0][1] is True
    assert "SSE detectado" in results[0][2]

@pytest.mark.asyncio
async def test_validate_servers_empty(mock_fs):
    mock_fs.exists.return_value = True
    config_data = {"mcpServers": {}}
    
    adapter = MCPValidatorAdapter(fs=mock_fs, config_path="/fake/path.json")
    
    with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(config_data))):
        results = await adapter.validate_servers()
        
    assert results[0][1] is True
    assert "No hay servidores" in results[0][2]

@pytest.mark.asyncio
async def test_validate_servers_unsupported(mock_fs):
    mock_fs.exists.return_value = True
    config_data = {
        "mcpServers": {
            "weird-server": {
                "transport": "magic"
            }
        }
    }
    
    adapter = MCPValidatorAdapter(fs=mock_fs, config_path="/fake/path.json")
    
    with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(config_data))):
        results = await adapter.validate_servers()
        
    assert results[0][1] is False
    assert "no soportado" in results[0][2]
