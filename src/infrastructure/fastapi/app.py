"""
Path: src/infrastructure/fastapi/app.py
"""

from fastapi import FastAPI, Request, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from typing import Optional, Any
from src.interface_adapters.controllers.telegram_controller import TelegramController
from src.infrastructure.fastapi.middleware import ObservabilityMiddleware

def create_app(controller: TelegramController, lifespan: Optional[Any] = None) -> FastAPI:
    app = FastAPI(
        title="Telegram Gemini CLI Bridge",
        lifespan=lifespan
    )

    # Añadir Middleware de Observabilidad
    app.add_middleware(ObservabilityMiddleware)

    @app.post("/webhook")
    async def webhook(request: Request, background_tasks: BackgroundTasks, x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
        try:
            data = await request.json()
            msg, trace_id = await controller.handle_webhook(data, x_telegram_bot_api_secret_token)
            
            if msg:
                background_tasks.add_task(controller.execute_task, msg, trace_id)
                
            return {"status": "ok"}
        except PermissionError:
            return JSONResponse(status_code=403, content={"status": "forbidden"})
        except Exception as e:
            # En el webhook no logueamos con el logger global para evitar ruido, 
            # pero el Trace ID ya debería estar en el contexto si llegó al controlador.
            return {"status": "error", "message": str(e)}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
