"""
Path: src/infrastructure/shell/asyncio_runner.py
"""

import asyncio
import os
from typing import List, Tuple, Optional
from src.use_cases.ports.interfaces import ShellGateway

class AsyncioShellRunner(ShellGateway):
    async def execute(self, args: List[str], env: Optional[dict] = None, cwd: Optional[str] = None, timeout: float = 30.0) -> Tuple[int, str, str]:
        """Implementación real usando el motor de asyncio de Python."""
        # Unir el entorno actual con las variables adicionales
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=full_env,
            cwd=cwd
        )
        
        try:
            # Usamos el timeout proporcionado (por defecto 30s)
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return process.returncode, stdout.decode().strip(), stderr.decode().strip()
        except asyncio.TimeoutError:
            # Si hay timeout, matamos el proceso
            try:
                process.kill()
            except Exception:
                pass
            return -1, "", f"Error: Tiempo de espera agotado (Timeout {timeout}s) al ejecutar el comando."
