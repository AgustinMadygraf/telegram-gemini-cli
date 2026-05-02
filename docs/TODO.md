# TODO - Telegram Gemini CLI Bridge

## Roadmap de Refactorización

### Fase 1: Reestructuración de Directorios (Inmediato)
- [ ] Mover entidades a `src/entities/`.
- [ ] Crear interfaces (ports) en `src/use_cases/gateways/`.
- [ ] Crear adaptadores de infraestructura en `src/infrastructure/`.
- [ ] Dividir adaptadores actuales en Controllers, Gateways e Implementaciones.
- [ ] Mover configuración a `src/infrastructure/setting/`.

### Fase 2: Implementación de la Lógica Desacoplada
- [ ] Implementar `TelegramController` (FastAPI -> Use Case).
- [ ] Implementar `GeminiGateway` (Use Case -> Shell).
- [ ] Implementar `TelegramPresenter` (Use Case -> Formateo).

### Fase 3: Observabilidad y Estabilidad
- [ ] Configurar Logger centralizado en `src/infrastructure/setting/logger.py`.
- [ ] Refinar las validaciones de arranque (Hard Exit).
- [ ] Implementar validación de secreto de Webhook en el Controller.

### Fase 4: Pruebas y despliegue
- [ ] Test de flujo completo: Webhook -> Controller -> Use Case -> Gateway -> Presenter -> Telegram.
- [ ] Configuración final de Cloudflare Tunnel.
