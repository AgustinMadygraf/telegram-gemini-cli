# Software Requirements Specification (SRS) - Telegram Gemini CLI Bridge

## 1. Introducción
El sistema "Telegram Gemini CLI Bridge" es un intermediario entre Telegram y `gemini-cli`, diseñado bajo una arquitectura de **Círculos Concéntricos (Clean Architecture / Hexagonal)** con abstracción total de dependencias de bajo nivel.

## 2. Certezas Técnicas
- **Stack**: Python, FastAPI, Cloudflare Tunnel.
- **Seguridad**: Whitelist de usuarios, validación de secretos de Webhook y **Hard Exit**.
- **Independencia del OS**: El núcleo no depende de `asyncio` o `os` directamente, sino de gateways de sistema.

## 3. Arquitectura Limpia y capas

### Capa 1: Entidades (src/entities)
- `ai.py`: Respuestas y estados de la IA.
- `chat.py`: Estructura de mensajes.
- `network.py`: Estado del Webhook y del Túnel.
- `validation.py`: Reportes de salud del sistema.

### Capa 2: Casos de Uso (src/use_cases)
- **Ports**: `MessengerGateway`, `AIEngineGateway`, `TunnelGateway`, `ShellGateway`, `FileSystemGateway`.
- **Interactors**: `ProcessMessage`, `SystemValidator`.

### Capa 3: Adaptadores de Interfaz (src/interface_adapters)
- **Controllers**: `TelegramController` (Puro Python).
- **Gateways**: `TelegramGateway`, `GeminiGateway`, `CloudflareGateway`. Todos libres de lógica de infraestructura.
- **Presenters**: Formateo de salida para el usuario final (Pendiente).

### Capa 4: Infraestructura (src/infrastructure)
- **fastapi/**: Servidor Web y traducción HTTP.
- **shell/**: Ejecución real de comandos (`asyncio`) y sistema de archivos (`os`).
- **setting/**: `config.py` y `logger.py`.

## 4. Validación de Salud (Deep Health Check)
El sistema valida secuencialmente:
1. **Credenciales**: Token de Bot y Binario de Gemini.
2. **Sistema**: Disponibilidad de binarios y permisos de archivos.
3. **Túnel**: Verificación de estado del túnel de Cloudflare.
4. **Red**: Sincronización automática de URL de Webhook en Telegram.
