# Software Requirements Specification (SRS) - Telegram Gemini CLI Bridge

## 1. Introducción
El sistema "Telegram Gemini CLI Bridge" es un intermediario entre Telegram y `gemini-cli`, diseñado bajo una arquitectura de **Círculos Concéntricos (Clean Architecture / Hexagonal)**.

## 2. Certezas Técnicas
- **Stack**: Python, FastAPI, Cloudflare Tunnel.
- **Seguridad**: Whitelist de usuarios, validación de secretos de Webhook y **Hard Exit**.
- **Auto-Sincronización**: El sistema registra automáticamente el Webhook en Telegram al arrancar si detecta discrepancias en la URL.

## 3. Arquitectura Limpia y capas

### Capa 1: Entidades (src/entities)
- `ai.py`: Respuestas y estados de la IA.
- `chat.py`: Estructura de mensajes.
- `network.py`: Estado del Webhook y del Túnel.

### Capa 2: Casos de Uso (src/use_cases)
Define los contratos (**Ports**) que el núcleo necesita.
- **Ports**: `MessengerGateway`, `AIEngineGateway`, `TunnelGateway`.
- **Interactors**: `ProcessMessage`, `SystemValidator`.

### Capa 3: Adaptadores de Interfaz (src/interface_adapters)
- **Controllers**: Mapeo de FastAPI a casos de uso.
- **Gateways**: Implementaciones concretas.
    - `TelegramGateway`: Mensajería y Webhook Info.
    - `GeminiGateway`: Interacción con CLI.
    - `CloudflareGateway`: Monitoreo del estado del túnel.
- **Presenters**: Formateo de salida para el usuario final.

### Capa 4: Infraestructura (src/infrastructure)
- **fastapi/**: Configuración del server.
- **setting/**: `config.py` y `logger.py`.

## 4. Validación de Salud y Red (Deep Health Check)
El sistema realiza un triple chequeo en el arranque:
1. **Credenciales**: Token de Bot y Binario de Gemini.
2. **Webhook**: Sincronización de URL en Telegram.
3. **Túnel**: Verificación de estado `Healthy` en la infraestructura de Cloudflare.
