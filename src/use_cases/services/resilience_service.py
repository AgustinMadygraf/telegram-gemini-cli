"""
Path: src/use_cases/services/resilience_service.py
"""

import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "CLOSED" # Funcionamiento normal
    OPEN = "OPEN"     # Circuito abierto (protección activa)
    HALF_OPEN = "HALF_OPEN" # Probando recuperación

class CircuitBreakerService:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0

    def can_execute(self) -> bool:
        """Verifica si el circuito permite la ejecución."""
        if self.state == CircuitState.OPEN:
            # Verificar si ya pasó el tiempo de recuperación
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def record_success(self):
        """Registra un éxito y resetea el contador."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        """Registra un fallo y abre el circuito si supera el umbral."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
