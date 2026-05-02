# TODO - Telegram Gemini CLI Bridge (Clean Architecture Edition)

## Roadmap de Desarrollo

### Fase 1: Estructura de Dominio y Aplicación
- [ ] Definir Entidades y Value Objects de dominio (`Chat`, `Message`, `Session`).
- [ ] Definir interfaces de servicios (contratos para `ChatProvider` y `AIEngine`).
- [ ] Implementar el Caso de Uso: `ProcessMessage`.

### Fase 2: Infraestructura (Adaptadores)
- [ ] Implementar `GeminiCLIAdapter` (Ejecución de subprocesos shell).
- [ ] Implementar `TelegramBotAdapter` (Integración con la librería `telegraf`).
- [ ] Configurar el sistema de logging desacoplado.

### Fase 3: Bootstrap (Orquestación)
- [ ] Crear el `Container` o script de inicialización que inyecte las dependencias.
- [ ] Configurar variables de entorno y validaciones de arranque.
- [ ] Implementar el sistema de seguridad (Whitelist Middleware).

### Fase 4: Refinamiento de Salida y UX
- [ ] Implementar `MessageSplitter` para cumplir con los límites de Telegram.
- [ ] Añadir soporte para comandos nativos (`/start`, `/reset`).
- [ ] Pruebas de integración con MCPs reales (Xubio/WooCommerce).

## Checklist de Calidad (SOLID)
- [ ] ¿Hay lógica de Telegram en el adaptador de Gemini? (Debe ser No).
- [ ] ¿Los casos de uso dependen de clases concretas? (Debe ser No).
- [ ] ¿Es fácil cambiar `gemini-cli` por otro modelo sin tocar el `ProcessMessage`? (Debe ser Sí).
