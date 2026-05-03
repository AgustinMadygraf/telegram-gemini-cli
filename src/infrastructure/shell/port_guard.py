"""
Path: src/infrastructure/shell/port_guard.py
"""

import socket
import os
import signal
import subprocess
from typing import Optional
from src.use_cases.ports.interfaces import LoggerPort

class PortGuard:
    def __init__(self, port: int, logger: LoggerPort):
        self.port = port
        self.logger = logger

    def is_port_in_use(self) -> bool:
        """Verifica si el puerto está ocupado."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', self.port)) == 0

    def clean_port(self) -> bool:
        """
        Si el puerto está en uso, intenta liberar el proceso.
        Retorna True si el puerto quedó libre.
        """
        if not self.is_port_in_use():
            return True

        self.logger.info(f"🔍 Puerto {self.port} ocupado. Intentando liberar...")
        
        try:
            # Buscamos el PID que ocupa el puerto (específico de Linux)
            cmd = f"lsof -t -i:{self.port}"
            pid_bytes = subprocess.check_output(cmd.split())
            pids = pid_bytes.decode().strip().split('\n')
            
            for pid_str in pids:
                if not pid_str: continue
                pid = int(pid_str)
                self.logger.warning(f"⚠️ Terminando proceso intruso (PID: {pid})...")
                os.kill(pid, signal.SIGTERM)
            
            # Esperar un momento a que el OS libere el socket
            import time
            time.sleep(1)
            
            if not self.is_port_in_use():
                self.logger.info(f"✅ Puerto {self.port} liberado exitosamente.")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ No se pudo liberar el puerto automáticamente: {e}")
            
        return not self.is_port_in_use()
