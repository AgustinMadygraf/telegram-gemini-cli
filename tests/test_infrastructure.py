"""
Path: tests/test_infrastructure.py
"""
import pytest
import os
import shutil
from unittest.mock import patch, MagicMock, AsyncMock
from src.infrastructure.shell.local_filesystem import LocalFileSystem
from src.infrastructure.shell.asyncio_runner import AsyncioShellRunner
from src.infrastructure.shell.port_guard import PortGuard
from src.infrastructure.shell.cloudflare_runner import CloudflareTunnelRunner

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def temp_dir():
    path = "tests/temp_infra"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

def test_local_filesystem(temp_dir):
    fs = LocalFileSystem()
    test_file = os.path.join(temp_dir, "test.txt")
    fs.write_text(test_file, "content")
    assert fs.read_text(test_file) == "content"
    assert fs.exists(test_file) is True
    
    # Test directorios
    src_dir = os.path.join(temp_dir, "src")
    dst_dir = os.path.join(temp_dir, "dst")
    fs.ensure_dir(src_dir)
    fs.write_text(os.path.join(src_dir, "file.txt"), "data")
    
    fs.copy_directory(src_dir, dst_dir)
    assert fs.exists(os.path.join(dst_dir, "file.txt")) is True
    
    fs.remove_directory(dst_dir)
    assert fs.exists(dst_dir) is False
    
    fs.delete(test_file)

@pytest.mark.asyncio
async def test_asyncio_shell_runner(mock_logger):
    shell = AsyncioShellRunner(logger=mock_logger)
    code, stdout, stderr = await shell.execute(["echo", "hello"])
    assert code == 0
    assert "hello" in stdout

def test_port_guard_logic(mock_logger):
    guard = PortGuard(port=8000, logger=mock_logger)
    with patch("subprocess.check_output") as mock_check, \
         patch("os.kill") as mock_kill, \
         patch.object(PortGuard, "is_port_in_use") as mock_in_use:
        
        mock_in_use.return_value = False
        assert guard.clean_port() is True
        
        mock_in_use.side_effect = [True, False]
        mock_check.return_value = b"9999\n"
        assert guard.clean_port() is True

def test_cloudflare_tunnel_runner_advanced(mock_logger):
    runner = CloudflareTunnelRunner(tunnel_name="test", local_url="http://localhost:8000", logger=mock_logger)
    with patch("subprocess.Popen") as mock_popen, \
         patch("os.killpg") as mock_killpg, \
         patch("os.getpgid") as mock_getpgid, \
         patch("builtins.open", MagicMock()):
        
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        runner.process = mock_process
        runner.stop_tunnel()
        assert runner.process is None

@pytest.mark.asyncio
async def test_cloudflare_tunnel_runner_validate_branches(mock_logger):
    runner = CloudflareTunnelRunner(tunnel_name="test", local_url="http://localhost:8000", logger=mock_logger)
    assert await runner.validate_tunnel() is False
    
    runner.process = MagicMock()
    runner.process.poll.return_value = None
    assert await runner.validate_tunnel() is True
