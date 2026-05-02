# TODO - Telegram Gemini CLI Bridge

## Roadmap de Desarrollo

### Fase 1: Estructura y Validación (Completado)
- [x] Restructuración Clean Architecture (Ports & Adapters).
- [x] Validación de arranque con Hard Exit.
- [x] Auto-registro de Webhook en Telegram.

### Fase 2: Red y Túneles (Prioridad Actual)
- [ ] Incorporar `CLOUDFLARE_TOKEN` en la configuración.
- [ ] Implementar `CloudflareGateway` para monitoreo de túnel.
- [ ] Validar latencia de red al inicio.

### Fase 3: Capa de Presentación
- [ ] Implementar `TelegramPresenter` (MarkdownV2).
- [ ] Manejo de fragmentación de mensajes largos (>4096 caracteres).

### Fase 4: Experiencia de Usuario
- [ ] Implementar comando `/reset` (limpieza de contexto).
- [ ] Implementar comando `/status` (diagnóstico de salud del bot).
