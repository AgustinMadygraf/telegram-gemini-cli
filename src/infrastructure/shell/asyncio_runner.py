"""
Path: src/infrastructure/shell/asyncio_runner.py
"""

import asyncio
import os
from typing import List, Tuple, Optional
from src.use_cases.ports.interfaces import ShellGateway

class AsyncioShellRunner(ShellGateway):
    async def execute(self, args: List[str], env: Optional[dict] = None, cwd: Optional[str] = None, timeout: float = 30.0) -> Tuple[int, str, str]:
        """Ejecución con streaming en tiempo real para observabilidad."""
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
        
        stdout_chunks = []
        stderr_chunks = []

        async def read_stream(stream, collection, prefix=""):
            while True:
                line = await stream.readline()
                if not line:
                    break
                decoded_line = line.decode().strip()
                if decoded_line:
                    # Imprimimos en tiempo real para observabilidad
                    print(f"  {prefix} {decoded_line}")
                    collection.append(decoded_line)

        try:
            # Ejecutamos la lectura de ambos flujos en paralelo con el timeout
            await asyncio.wait_for(
                asyncio.gather(
                    read_stream(process.stdout, stdout_chunks, "stdout>"),
                    read_stream(process.stderr, stderr_chunks, "stderr>")
                ),
                timeout=timeout
            )
            await process.wait()
            return process.returncode, "\n".join(stdout_chunks), "\n".join(stderr_chunks)
        except asyncio.TimeoutError:
            try:
                process.kill()
            except Exception:
                pass
            return -1, "\n".join(stdout_chunks), f"Error: Tiempo de espera agotado (Timeout {timeout}s)"
