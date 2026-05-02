# Discovery & Open Questions

## Certezas del Diseño

1. **Abstracción de Sistema**: Se ha implementado `ShellGateway` para desacoplar la ejecución de comandos de `asyncio`, logrando excelencia técnica y testabilidad.
2. **Eliminación de Logs en Adapters**: Se ha decidido que los Gateways y Controllers sean silenciosos, delegando el reporte al `ValidationReport`.
3. **Sincronización Automática**: El bot se encarga de configurar su propio Webhook en Telegram al arrancar.

## Dudas Actuales

### 1. Formateo de Respuesta (Presenter)
- **Afirmación**: El formateo de MarkdownV2 en Telegram requiere escapar caracteres como `_`, `*`, `[`, `]`, `(`, `)`, `~`, `> `, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`.
- **Duda**: ¿Debemos implementar un parser que convierta el Markdown estándar de Gemini a MarkdownV2 de Telegram de forma automática?

### 2. Gestión de Sesión Multi-usuario
- **Afirmación**: Actualmente usamos `--resume latest` en Gemini CLI.
- **Duda**: ¿Cómo evitar que los contextos de diferentes usuarios se mezclen si Gemini CLI no soporta IDs de sesión nativos por separado en esta versión?

### 3. Latencia del Túnel
- **Afirmación**: Cloudflare Tunnel puede añadir latencia.
- **Duda**: ¿Deberíamos implementar un sistema de "ACK" (confirmación) rápido en el webhook para evitar reintentos de Telegram mientras Gemini procesa la respuesta?
