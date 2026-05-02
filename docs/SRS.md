# Software Requirements Specification (SRS) - Telegram Gemini CLI Bridge

## 1. Introducción
El sistema "Telegram Gemini CLI Bridge" actúa como un intermediario entre la API de Telegram y el ejecutable local `gemini-cli`. Su diseño se basa en **Clean Architecture**, **SOLID** y **Domain-Driven Design (DDD)** para garantizar la mantenibilidad y extensibilidad.

## 2. Certezas Técnicas (Technical Certainties)

1. **Entorno Local**: `gemini-cli` es el motor de inferencia y ejecución de herramientas.
2. **Backends MCP**: Acceso a `xubio` y `woocommerce` a través de la CLI.
3. **Persistencia**: Uso de `--resume latest` para mantener el contexto del hilo de conversación.
4. **Seguridad**: Whitelist de `chat_id` como primer nivel de defensa.

## 3. Arquitectura Limpia (Clean Architecture)

El proyecto se estructurará en capas concéntricas para desacoplar la lógica de negocio de los detalles de infraestructura:

### Capa de Dominio (Domain)
- **Entidades**: `Message`, `ChatSession`, `Command`.
- **Value Objects**: `TelegramId`, `Prompt`.
- **Interfaces**: `GeminiService`, `ChatProvider`.

### Capa de Aplicación (Application / Use Cases)
- **Casos de Uso**: 
    - `ProcessIncomingMessage`: Coordina la recepción de un mensaje de Telegram y su envío a Gemini.
    - `ResetChatSession`: Limpia el contexto de la conversación.
    - `HandleToolOutput`: (Futuro) Gestiona la lógica específica para resultados de herramientas MCP.

### Capa de Infraestructura (Infrastructure)
- **TelegramProvider**: Implementación concreta usando `Telegraf`.
- **GeminiCLIProvider**: Adaptador que ejecuta el binario de sistema `gemini`.
- **PersistenceAdapter**: Manejo de variables de entorno y estados locales.

## 4. Principios SOLID Aplicados

- **S (Single Responsibility)**: El adaptador de Gemini solo se encarga de la ejecución del comando; no conoce la lógica de Telegram.
- **O (Open/Closed)**: El sistema permite añadir nuevos "Providers" de chat (ej: WhatsApp) sin modificar el caso de uso principal.
- **L (Liskov Substitution)**: Cualquier implementación de `ChatProvider` debe ser intercambiable.
- **I (Interface Segregation)**: Las interfaces de dominio son específicas para las necesidades de los casos de uso.
- **D (Dependency Inversion)**: Los casos de uso dependen de interfaces (abstracciones), no de las implementaciones concretas de infraestructura.

## 5. Diseño del Dominio (DDD)

### Ubiquitous Language
- **Prompt**: El texto procesado que se envía a Gemini.
- **Turn**: Una interacción completa (Mensaje del usuario -> Respuesta de la IA).
- **Session**: El hilo continuo de "Turns" persistido en Gemini.

### Bounded Contexts
- **Chat Context**: Gestión de usuarios, comandos de Telegram y formatos de salida.
- **AI Context**: Gestión de la ejecución de Gemini, manejo de MCPs y control de sesiones.
