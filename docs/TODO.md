# TODO - Telegram Gemini CLI Bridge

## Roadmap de Desarrollo

### Fase 1: Estructura y Validación (Completado)
- [x] Restructuración Clean Architecture (Ports & Adapters).
- [x] Validación de arranque con Hard Exit.
- [x] Auto-registro de Webhook en Telegram.

### Fase 2: Red, Túneles y OS (Completado)
- [x] Implementar `CloudflareGateway`.
- [x] **Abstracción total del sistema (Shell & FileSystem)**.
- [x] Eliminación de dependencias de infraestructura en Adapters.

### Fase 3: Capa de Presentación (Prioridad Actual)
- [ ] Implementar `TelegramPresenter` (Manejo de MarkdownV2).
- [ ] Escapar caracteres especiales automáticamente.
- [ ] Manejo de fragmentación de mensajes largos (>4096 caracteres).

### Fase 4: Experiencia y Comandos
- [ ] Implementar comando `/reset` (limpieza de contexto).
- [ ] Implementar comando `/status` (diagnóstico de salud).
