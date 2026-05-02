"""
Path: src/infrastructure/shell/cloudflare_runner.py
"""

import subprocess
import time
import os
import signal
from typing import Optional
from src.use_cases.ports.interfaces import TunnelGateway

class CloudflareTunnelRunner(TunnelGateway):
    def __init__(self, tunnel_name: str, local_url: str):
        self.tunnel_name = tunnel_name
        self.local_url = local_url
        self.process: Optional[subprocess.Popen] = None

    async def validate_tunnel(self, url: Optional[str] = None) -> bool:
        """
        Verifica si el proceso del túnel está vivo.
        """
        if not (self.process and self.process.poll() is None):
            return False

        # 2. Verificar Resolución de Host (Opcional)
        if url:
            try:
                from urllib.parse import urlparse
                import socket
                
                hostname = urlparse(url).hostname
                if hostname:
                    # Intenta resolver el host para asegurar que el túnel está propagado
                    socket.gethostbyname(hostname)
                    return True
            except Exception:
                return False # No resuelve o error de parseo
        
        return True

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

        # Iniciamos el proceso sin bloquear, guardando logs para diagnóstico
        log_path = "tunnel.log"
        log_file = open(log_path, "a")
        
        self.process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            preexec_fn=os.setsid
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
