# TODO - Telegram Gemini CLI Bridge

## Roadmap de Desarrollo

### Fase 1: Estructura y Validación (Completado)
- [x] Restructuración Clean Architecture (Ports & Adapters).
- [x] Validación de arranque con Hard Exit.
- [x] Encabezados de ruta y documentación unificada.

### Fase 2: Salud y Red (Prioridad Actual)
- [ ] Implementar `getWebhookInfo` en el validador de Telegram.
- [ ] Validar latencia y conectividad del túnel al inicio.
- [ ] Agregar endpoint de diagnóstico detallado.

### Fase 3: Lógica de Aplicación y Presentación
- [ ] Implementar `TelegramPresenter` (MarkdownV2 escaping).
- [ ] Manejo de fragmentación inteligente de mensajes largos.
- [ ] Comando `/reset` para limpiar contexto de Gemini.

### Fase 4: Soporte Multi-usuario y Sesiones
- [ ] Investigar manejo de sesiones independientes en Gemini CLI.
- [ ] Implementar persistencia de metadatos de usuario.
