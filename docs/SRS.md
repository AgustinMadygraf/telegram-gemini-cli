# Software Requirements Specification (SRS) - Telegram Gemini CLI Bridge

## 1. Introducción
El sistema "Telegram Gemini CLI Bridge" es un intermediario entre Telegram y `gemini-cli`, diseñado bajo una arquitectura de **Círculos Concéntricos (Clean Architecture / Hexagonal)**.

## 2. Certezas Técnicas
- **Stack**: Python, FastAPI, Cloudflare Tunnel.
- **AI Core**: Gemini CLI via Shell Adapter (`subprocess`).
- **Seguridad**: Whitelist de usuarios, validación de secretos de Webhook y **Hard Exit** en fallos de arranque.

## 3. Arquitectura Limpia y capas

### Capa 1: Entidades (src/entities)
Objetos de negocio puros.
- `ai.py`: Respuestas y estados de la IA.
- `chat.py`: Estructura de mensajes y usuarios.

### Capa 2: Casos de Uso (src/use_cases)
Lógica de la aplicación y definición de **Ports**.
- **Ports (Interfaces)**: `interfaces.py` define los contratos `MessengerGateway`, `AIEngineGateway`, etc.
- **Interactors**: `ProcessMessage`, `SystemValidator`.

### Capa 3: Adaptadores de Interfaz (src/interface_adapters)
Mapeo entre el núcleo y el mundo exterior.
- **Controllers**: Mapeo de HTTP/FastAPI a casos de uso.
- **Gateways**: Implementaciones concretas de los puertos (Gemini y Telegram).
- **Presenters**: Formateo de salida (pendiente de implementación).

### Capa 4: Infraestructura (src/infrastructure)
Detalles técnicos y configuración.
- **fastapi/**: Configuración del server.
- **setting/**: `config.py` y `logger.py`.

## 4. Validación de Salud y Red
El sistema debe verificar no solo que las credenciales son válidas, sino que la comunicación bidireccional (Outbound y Inbound) es posible a través del túnel.
