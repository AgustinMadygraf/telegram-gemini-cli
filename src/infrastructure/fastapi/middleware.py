"""
Path: src/infrastructure/fastapi/middleware.py
"""

import time
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("infrastructure.network")

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            # Procesar la petición
            response = await call_next(request)
            
            # Loguear métricas básicas de éxito
            process_time = time.time() - start_time
            if request.url.path != "/health":
                logger.info(f"REQ: {request.method} {request.url.path} | STATUS: {response.status_code} | TIME: {process_time:.4f}s")
            
            return response

        except PermissionError as e:
            # Captura errores de seguridad lanzados por el controlador
            logger.warning(f"AUDIT SECURITY: Intento de acceso no autorizado en {request.url.path} - {str(e)}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden"}
            )
            
        except Exception as e:
            # Captura errores no controlados
            process_time = time.time() - start_time
            logger.error(f"SYSTEM ERROR: {request.method} {request.url.path} | ERROR: {str(e)} | TIME: {process_time:.4f}s")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )
