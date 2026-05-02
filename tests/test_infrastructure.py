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
    fs.delete("non_existent_file_123") # Cover exists check in delete

@pytest.mark.asyncio
async def test_asyncio_shell_runner():
    shell = AsyncioShellRunner()
    code, stdout, stderr = await shell.execute(["echo", "hello"])
    assert code == 0
    assert "hello" in stdout
    # Line 16 coverage: empty stderr is usually covered, but let's ensure
    assert stderr == ""

def test_port_guard_logic():
    guard = PortGuard(port=8000)
    
    with patch("subprocess.check_output") as mock_check, \
         patch("os.kill") as mock_kill, \
         patch.object(PortGuard, "is_port_in_use") as mock_in_use:
        
        # Caso: Puerto ya libre (Line 26)
        mock_in_use.return_value = False
        assert guard.clean_port() is True
        
        # Caso: Error al ejecutar lsof (Line 48-51)
        mock_in_use.return_value = True
        mock_check.side_effect = Exception("lsof failed")
        assert guard.clean_port() is False # Sigue ocupado
        
        # Caso: Matar proceso exitosamente
        mock_in_use.side_effect = [True, False]
        mock_check.side_effect = None
        mock_check.return_value = b"9999\n"
        assert guard.clean_port() is True

def test_cloudflare_tunnel_runner_advanced():
    runner = CloudflareTunnelRunner(tunnel_name="test", local_url="http://localhost:8000")
    
    with patch("subprocess.Popen") as mock_popen, \
         patch("os.killpg") as mock_killpg, \
         patch("os.getpgid") as mock_getpgid, \
         patch("builtins.open", MagicMock()):
        
        mock_process = MagicMock()
        mock_process.pid = 1234
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        # Caso: Ya está corriendo (Line 44)
        runner.process = mock_process
        runner.start_tunnel()
        assert mock_popen.call_count == 0
        
        # Caso: Error al detener (Line 78-80)
        mock_killpg.side_effect = Exception("OS Error")
        runner.stop_tunnel()
        assert mock_process.kill.called
        assert runner.process is None

@pytest.mark.asyncio
async def test_cloudflare_tunnel_runner_validate_branches():
    runner = CloudflareTunnelRunner(tunnel_name="test", local_url="http://localhost:8000")
    # Caso: Sin proceso (Line 23)
    assert await runner.validate_tunnel() is False
    
    # Caso: Proceso vivo pero sin URL (Line 39)
    runner.process = MagicMock()
    runner.process.poll.return_value = None
    assert await runner.validate_tunnel() is True
