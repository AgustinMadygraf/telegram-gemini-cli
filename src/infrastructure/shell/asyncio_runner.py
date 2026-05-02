"""
Path: src/infrastructure/shell/asyncio_runner.py
"""

import asyncio
from typing import List, Tuple
from src.use_cases.ports.interfaces import ShellGateway

class AsyncioShellRunner(ShellGateway):
    async def execute(self, args: List[str]) -> Tuple[int, str, str]:
        """Implementación real usando el motor de asyncio de Python."""
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode().strip(), stderr.decode().strip()
