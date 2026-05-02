# Arquitectura del Sistema

El proyecto implementa los principios de **Clean Architecture** (Arquitectura Hexagonal) y **Domain-Driven Design (DDD)** para garantizar el desacoplamiento total de la lógica de negocio frente a la infraestructura.

## Las 4 Capas

### 1. Entidades (`src/entities`)
Son el núcleo del sistema. Contienen los objetos de negocio puros y validaciones que no dependen de ninguna base de datos ni framework.
*   `ChatMessage`: Representa un mensaje de entrada de cualquier plataforma.
*   `AIResponse`: Respuesta unificada de cualquier motor de IA.
*   `ValidationReport`: Resultado detallado de la salud del sistema.

### 2. Casos de Uso (`src/use_cases`)
Contienen las reglas de aplicación. Orquestan el flujo de datos desde y hacia las entidades.
*   `ProcessMessageUseCase`: Recibe un mensaje, valida al usuario, consulta a la IA y formatea la respuesta.
*   `SystemValidatorService`: Coordina los diferentes validadores (IA, Red, Túnel) para asegurar el arranque.

### 3. Adaptadores de Interfaz (`src/interface_adapters`)
Traductores entre el mundo exterior y la aplicación.
*   **Gateways**: Implementaciones de los puertos definidos en `use_cases/ports`.
    *   `GeminiCLIAdapter`: Se comunica con el binario de Gemini.
    *   `TelegramAdapter`: Se comunica con la API de Telegram.
*   **Presenters**: Formatean la salida para plataformas específicas (ej: convertir Markdown de Gemini a HTML de Telegram).
*   **Controllers**: Reciben los webhooks de FastAPI y los transforman en entidades de dominio.

### 4. Infraestructura (`src/infrastructure`)
Detalles técnicos y herramientas de bajo nivel.
*   **FastAPI**: Servidor web y middleware de observabilidad.
*   **Shell**: Ejecución asíncrona de comandos del sistema.
*   **PortGuard**: Herramienta de limpieza de puertos.

---

## Flujo de una Petición (Request Lifecycle)

1.  **FastAPI** recibe un `POST /webhook`.
2.  **ObservabilityMiddleware** inicia el cronómetro y loguea la entrada.
3.  **TelegramController** valida el `secret_token` y transforma el JSON en un `ChatMessage`.
4.  **ProcessMessageUseCase** valida si el `user_id` está en la whitelist.
5.  **GeminiCLIAdapter** prepara el entorno aislado en `storage/sessions/` y ejecuta el comando.
6.  **TelegramPresenter** escapa caracteres conflictivos y fragmenta el texto si excede los 4096 caracteres.
7.  **TelegramAdapter** envía la respuesta final al usuario.

---

## Observabilidad y Trazabilidad

El sistema no solo loguea peticiones HTTP, sino que aplica una política de **Falla Visible**:
*   **Trazabilidad de Payloads**: Ante un error `400 Bad Request` de Telegram, el sistema captura y loguea el HTML exacto que causó el conflicto para facilitar el ajuste del Presenter.
*   **Middleware de Auditoría**: Cada webhook es rastreado con su tiempo de ejecución y resultado, permitiendo detectar cuellos de botella en la IA.
