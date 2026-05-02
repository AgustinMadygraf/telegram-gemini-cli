# Discovery & Open Questions - Arquitectura y Diseño

## Decisiones Técnicas Tomadas (Certezas)

- **Lenguaje**: Python (FastAPI).
- **Transporte**: Webhook + Cloudflare Tunnel.
- **Seguridad**: Validación de `X-Telegram-Bot-Api-Secret-Token` (recomendado por Telegram para webhooks).
- **Orquestación**: Subprocesos de Python para invocar la CLI de Gemini.

## Nuevos Puntos de Investigación (Dudas)

### 1. Configuración de Cloudflare Tunnel
- **Duda**: ¿Usar túneles "Managed" (vía dashboard de Cloudflare) o "Local-managed" (vía archivo `config.yml`)?
- **Preferencia**: El modo local permite versionar la configuración, pero el modo managed es más sencillo de mantener.

### 2. Sincronía del Webhook vs Respuesta de Gemini
- **Duda**: Telegram espera una respuesta rápida (200 OK) al recibir el webhook. Sin embargo, Gemini + MCP puede tardar 20-30 segundos.
- **Investigación**: ¿Debemos responder 200 OK inmediatamente y enviar la respuesta de Gemini de forma asíncrona usando una tarea de fondo (`BackgroundTasks` de FastAPI)?
- **Análisis**: Sí, es imperativo usar tareas de fondo para evitar que Telegram reintente el envío del mensaje por timeout.

### 3. Gestión de Secretos en Python
- **Duda**: ¿Uso de `python-dotenv` vs `pydantic-settings`?
- **Decisión**: `pydantic-settings` es el estándar moderno en FastAPI para validación de configuraciones.

### 4. Formateo de Markdown en Telegram
- **Duda**: Gemini suele devolver MarkdownV2. Telegram es muy estricto con el escape de caracteres en MarkdownV2.
- **Investigación**: Validar si es mejor usar `parse_mode='HTML'` o implementar una función robusta de escape para MarkdownV2.
