# Discovery & Open Questions

## Certezas del Diseño

1. **Abstracción de Sistema**: Se ha implementado `ShellGateway` y `FileSystemGateway`. Los adaptadores son ahora 100% agnósticos al OS.
2. **Hard Exit Verificado**: El sistema detiene correctamente el arranque ante fallos de red o credenciales.
3. **Observabilidad Centralizada**: Middleware de infraestructura gestiona auditoría y traducción de errores.

## Hallazgos Técnicos

### 1. Fallo setWebhook (400 Bad Request) - RESUELTO
- **Observación**: Telegram rechazaba el webhook por fallo en la resolución del host.
- **Solución**: Se instaló `cloudflared` en el sistema. El túnel debe estar activo para que el dominio sea resoluble por Telegram.

## Dudas Actuales

### 1. Rigor del Túnel en Desarrollo
- **Decisión**: Se ha flexibilizado la validación del túnel para permitir el arranque con `Warning` si el token falta, facilitando el desarrollo local.

### 2. Multi-usuario y Contexto - RESUELTO
- **Observación**: Gemini CLI requiere UUIDs para el flag `--resume`, lo que dificultaba el uso directo de `chat_id`.
- **Solución**: Se utiliza la variable de entorno `GEMINI_CLI_HOME` para aislar el contexto de cada usuario en un directorio separado (`/tmp/gemini_sessions/{chat_id}`). Esto garantiza que cada conversación sea independiente y persistente sin riesgo de cruce.
