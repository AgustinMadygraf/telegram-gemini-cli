"""
Path: src/infrastructure/shell/cloudflare_runner.py
"""

import subprocess
import time
import os
import signal
from src.use_cases.ports.interfaces import TunnelGateway

class CloudflareTunnelRunner(TunnelGateway):
    def __init__(self, tunnel_name: str, local_url: str):
        self.tunnel_name = tunnel_name
        self.local_url = local_url
        self.process: Optional[subprocess.Popen] = None

    async def validate_tunnel(self) -> bool:
        """
        Verifica si el proceso del túnel está vivo.
        En una versión más avanzada, podríamos consultar la API de métricas de cloudflared.
        """
        return self.process is not None and self.process.poll() is None

    def start_tunnel(self) -> None:
        """Inicia el túnel de Cloudflare en segundo plano."""
        if self.process and self.process.poll() is None:
            return # Ya está corriendo

        print(f"🚀 Iniciando túnel Cloudflare: {self.tunnel_name} -> {self.local_url}")
        
        # Comando para correr el túnel por nombre (usando el cert.pem local)
        cmd = [
            "cloudflared", "tunnel", "run", 
            "--url", self.local_url,
            self.tunnel_name
        ]

        # Iniciamos el proceso sin bloquear
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL, # Mantenemos la consola limpia, o podríamos loguear a archivo
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid # Permite matar a todo el grupo de procesos después
        )
        
        # Esperar un momento a que el túnel intente conectar
        time.sleep(2)

    def stop_tunnel(self) -> None:
        """Detiene el proceso del túnel de forma segura."""
        if self.process and self.process.poll() is None:
            print(f"🛑 Deteniendo túnel Cloudflare ({self.tunnel_name})...")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
            except Exception:
                if self.process:
                    self.process.kill()
            print("✅ Túnel detenido.")
