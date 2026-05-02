# TODO - Telegram Gemini CLI Bridge (Python + FastAPI Edition)

## Roadmap de Desarrollo

### Fase 1: Estructura Pythonic
- [ ] Crear entorno virtual y `requirements.txt` (`fastapi`, `uvicorn`, `pydantic-settings`, `httpx`).
- [ ] Configurar `config.py` con Pydantic Settings.
- [ ] Definir el dominio: `entities.py` y `interfaces.py`.

### Fase 2: Adaptadores e Infraestructura
- [ ] Implementar `GeminiCLIAdapter` usando `asyncio.create_subprocess_exec`.
- [ ] Configurar FastAPI con un endpoint `/webhook`.
- [ ] Implementar cliente `httpx` para enviar respuestas a Telegram de forma asíncrona.

### Fase 3: Túnel y Webhook
- [ ] Instalar y configurar `cloudflared`.
- [ ] Obtener el dominio del túnel y configurar el webhook en Telegram (`setWebhook`).
- [ ] Implementar validación de secreto del webhook para seguridad.

### Fase 4: UX y MCPs
- [ ] Manejar estados de "typing..." mientras Gemini procesa.
- [ ] Implementar lógica de fragmentación de mensajes.
- [ ] Test final con Xubio y WooCommerce.

---
*Para ver las dudas técnicas pendientes, consultar [DISCOVERY.md](docs/DISCOVERY.md)*.
