# Discovery & Open Questions

## Certezas del Diseño

1. **Abstracción de Sistema**: Se ha implementado `ShellGateway` y `FileSystemGateway`. Los adaptadores son ahora 100% agnósticos al OS.
2. **Hard Exit Verificado**: En la ejecución del 2026-05-02 12:15, el sistema detuvo correctamente el arranque ante un fallo de red (`400 Bad Request` de Telegram), validando la resiliencia del diseño.
3. **Observabilidad Centralizada**: El uso de un `Middleware` de infraestructura elimina la necesidad de `import logging` en el resto del sistema.

## Hallazgos Técnicos

### 1. Fallo setWebhook (400 Bad Request)
- **Observación**: Telegram rechazó la sincronización automática del Webhook.
- **Hipótesis**: El `WEBHOOK_SECRET_TOKEN` podría contener caracteres inválidos o la `WEBHOOK_URL` requiere un túnel activo para ser validada por Telegram.

## Dudas Actuales

### 1. Rigor del Túnel en Desarrollo
- **Duda**: ¿Deberíamos permitir que el sistema arranque si el túnel falla pero estamos en modo "Desarrollo"? Actualmente el Hard Exit es total.

### 2. Multi-usuario y Contexto
- **Afirmación**: Usamos `--resume latest`.
- **Duda**: Es crítico investigar si Gemini CLI soporta archivos de sesión por `chat_id` para evitar cruce de conversaciones.
