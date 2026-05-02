# Software Requirements Specification (SRS) - Telegram Gemini CLI Bridge

## 1. Introducción
El sistema "Telegram Gemini CLI Bridge" es un intermediario entre Telegram y `gemini-cli`, diseñado bajo una arquitectura de **Círculos Concéntricos (Clean Architecture)**.

## 2. Certezas Técnicas
- **Stack**: Python, FastAPI, Cloudflare Tunnel.
- **AI Core**: Gemini CLI via Shell Adapter (`subprocess`).
- **Seguridad**: Whitelist de usuarios y validación de secretos de Webhook.

## 3. Arquitectura Limpia y capas

### Capa 1: Entidades (src/entities)
Contiene los objetos de negocio puros, libres de cualquier dependencia de frameworks.
- `Message`, `User`, `Session`.

### Capa 2: Casos de Uso (src/use_cases)
Contiene la lógica de la aplicación y define los contratos (**Ports/Interfaces**) que necesita para interactuar con el mundo exterior.
- **Gateways (Interfaces)**: `AIEngineGateway`, `MessengerGateway`.
- **Interactors**: `ProcessMessage`, `ResetSession`.

### Capa 3: Adaptadores de Interfaz (src/interface_adapters)
Mapea los datos entre los casos de uso y la infraestructura.
- **Controllers**: Manejan la lógica de entrada de FastAPI.
- **Gateways (Implementaciones)**: Adaptadores que implementan las interfaces de los casos de uso.
- **Presenters**: Dan formato a las respuestas de la IA para que sean compatibles con Telegram (Markdown, fragmentación).

### Capa 4: Infraestructura (src/infrastructure)
Contiene las herramientas y configuraciones de bajo nivel.
- **fastapi/**: Configuración del server y rutas.
- **telegram/**: Cliente de la API de Telegram.
- **setting/**: `config.py` y `logger.py`.

## 4. Flujo de Datos (Control Flow)
1. **Infraestructura (FastAPI)** recibe un Webhook.
2. El **Controller** convierte el JSON en una **Entidad de Dominio**.
3. El **Use Case** procesa la entidad, consultando al **AIGateway** (Abstracción).
4. El **Gateways (Impl)** ejecuta el comando de Gemini y devuelve el resultado.
5. El **Presenter** formatea el resultado.
6. El **Use Case** ordena el envío a través del **MessengerGateway**.
