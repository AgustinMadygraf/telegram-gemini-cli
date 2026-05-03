# TODO - Telegram Gemini CLI Bridge

## Roadmap de Desarrollo

### Fase 1: Estructura y Validación (Completado)
- [x] Restructuración Clean Architecture (Ports & Adapters).
- [x] Validación de arranque con Hard Exit.
- [x] Auto-registro de Webhook en Telegram.

### Fase 2: Red, Túneles y OS (Completado)
- [x] Implementar `CloudflareGateway`.
- [x] Abstracción total del sistema (Shell & FileSystem).
- [x] Middleware de Observabilidad.

### Fase 3: Capa de Presentación (Completado)
- [x] Implementar `TelegramPresenter` (Manejo de MarkdownV2).
- [x] Escapar caracteres especiales automáticamente.
- [x] Manejo de fragmentación de mensajes largos (>4096 caracteres).

### Fase 4: Robustez y Operación (Completado)
- [x] Iniciar túnel de Cloudflare y verificar resolución de host.
- [x] Cambiar `ALLOWED_CHAT_IDS` por ID real del usuario.
- [x] Implementar comando `/reset` (limpieza de contexto).
- [x] Manejo de sesiones multi-usuario.

### Fase 5: Ecosistema MCP (Completado)
- [x] Implementar `MCPValidator` en el `SystemValidatorService`.
- [x] Verificación de binarios STDIO declarados en `settings.json`.
- [x] Health check de endpoints SSE/HTTP.
- [x] Generación de Reporte de Acción (Sugerencias de reparación).
