# Discovery & Open Questions - Arquitectura y Diseño

Este documento analiza las dudas técnicas bajo la lente de DDD y Clean Architecture.

## Puntos de Investigación con Enfoque Arquitectónico

### 1. Desacoplamiento de Gemini CLI (SOLID: D)
- **Investigación**: ¿Cómo abstraer la ejecución de `gemini -p` para que en el futuro podamos migrar a una integración directa por SDK si fuera necesario?
- **Enfoque**: Crear una interfaz `AIEngine` en la capa de dominio. La implementación actual será `GeminiCLIAdapter`.

### 2. Gestión de Estados de Sesión (DDD: Aggregate Roots)
- **Duda**: ¿Debe la `ChatSession` ser el agregado raíz que gestione tanto el estado de Telegram como el de Gemini?
- **Análisis**: Mantener el estado de la sesión lo más liviano posible en el Bridge, delegando la persistencia histórica al flag `--resume latest` de Gemini, pero manteniendo un registro local de `LastInteraction` para timeouts.

### 3. Manejo de Errores y Excepciones (Clean Arch)
- **Duda**: ¿Cómo propagar errores de ejecución de comandos (ej: fallo de red en un MCP) hacia la UI de Telegram?
- **Enfoque**: Definir excepciones de dominio (ej: `AIServiceUnavailableException`) que el adaptador de infraestructura mapee desde el `stderr` de la CLI.

### 4. Fragmentación de Mensajes (SOLID: S)
- **Duda**: ¿Quién es responsable de dividir un mensaje largo?
- **Decisión**: No es responsabilidad del caso de uso. Debe ser un `OutputFormatter` en la capa de infraestructura o un decorador del `ChatProvider`.

## Decisiones Técnicas Tomadas (Certezas)

- **Patrón Adapter**: Se usará para todas las dependencias externas (Telegram API, Shell Execution).
- **Inyección de Dependencias**: El punto de entrada (`index.ts`) orquestará la creación y vinculación de los componentes de infraestructura con los casos de uso.
- **Domain First**: Empezaremos definiendo los tipos y contratos de dominio antes de tocar la API de Telegram.
