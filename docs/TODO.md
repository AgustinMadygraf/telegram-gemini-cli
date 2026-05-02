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

### Fase 4: Robustez y Operación
- [ ] Iniciar túnel de Cloudflare y verificar resolución de host.
- [ ] Cambiar `ALLOWED_CHAT_IDS` por ID real del usuario.
- [ ] Implementar comando `/reset` (limpieza de contexto).
- [ ] Manejo de sesiones multi-usuario.
