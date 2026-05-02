"""
Path: src/infrastructure/shell/port_guard.py
"""

import socket
import os
import signal
import subprocess
from typing import Optional

class PortGuard:
    def __init__(self, port: int):
        self.port = port

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

        print(f"🔍 Puerto {self.port} ocupado. Intentando liberar...")
        
        try:
            # Buscamos el PID que ocupa el puerto (específico de Linux)
            cmd = f"lsof -t -i:{self.port}"
            pid_bytes = subprocess.check_output(cmd.split())
            pid = int(pid_bytes.decode().strip())
            
            if pid:
                print(f"⚠️ Terminando proceso intruso (PID: {pid})...")
                os.kill(pid, signal.SIGTERM)
                
                # Esperar un momento a que el OS libere el socket
                import time
                time.sleep(1)
                
                if not self.is_port_in_use():
                    print(f"✅ Puerto {self.port} liberado exitosamente.")
                    return True
                    
        except Exception as e:
            print(f"❌ No se pudo liberar el puerto automáticamente: {e}")
            
        return not self.is_port_in_use()
