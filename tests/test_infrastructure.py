import pytest
import os
import shutil
import signal
from unittest.mock import patch, MagicMock
from src.infrastructure.shell.local_filesystem import LocalFileSystem
from src.infrastructure.shell.asyncio_runner import AsyncioShellRunner
from src.infrastructure.shell.port_guard import PortGuard
from src.infrastructure.shell.cloudflare_runner import CloudflareTunnelRunner

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
    
    fs.write_file(test_file, "content")
    assert fs.read(test_file) == "content"
    assert fs.exists(test_file) is True
    
    fs.ensure_dir(os.path.join(temp_dir, "subdir"))
    assert os.path.isdir(os.path.join(temp_dir, "subdir"))
    
    fs.delete(test_file)
    assert fs.exists(test_file) is False

@pytest.mark.asyncio
async def test_asyncio_shell_runner():
    shell = AsyncioShellRunner()
    code, stdout, stderr = await shell.execute(["echo", "hello"])
    assert code == 0
    assert "hello" in stdout

def test_port_guard_killing_logic():
    guard = PortGuard(port=8000)
    
    with patch("subprocess.check_output") as mock_check, \
         patch("os.kill") as mock_kill, \
         patch.object(PortGuard, "is_port_in_use") as mock_in_use:
        
        mock_in_use.side_effect = [True, False]
        mock_check.return_value = b"9999\n"
        
        success = guard.clean_port()
        
        assert success is True
        mock_kill.assert_called_once_with(9999, signal.SIGTERM)

def test_cloudflare_tunnel_runner_start_stop():
    runner = CloudflareTunnelRunner(tunnel_name="test", local_url="http://localhost:8000")
    
    with patch("subprocess.Popen") as mock_popen, \
         patch("os.killpg") as mock_killpg, \
         patch("os.getpgid") as mock_getpgid, \
         patch("builtins.open", MagicMock()):
        
        mock_process = MagicMock()
        mock_process.pid = 1234
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        runner.start_tunnel()
        assert runner.process is not None
        
        runner.stop_tunnel()
        assert mock_killpg.called
        assert runner.process is None

@pytest.mark.asyncio
async def test_cloudflare_tunnel_runner_validate():
    runner = CloudflareTunnelRunner(tunnel_name="test", local_url="http://localhost:8000")
    runner.process = MagicMock()
    runner.process.poll.return_value = None
    
    with patch("socket.gethostbyname") as mock_dns:
        mock_dns.return_value = "1.2.3.4"
        assert await runner.validate_tunnel("http://test.com") is True
        
        mock_dns.side_effect = Exception("not found")
        assert await runner.validate_tunnel("http://test.com") is False
