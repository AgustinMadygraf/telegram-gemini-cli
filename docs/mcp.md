# Model Context Protocol (MCP) Integration Strategy

Este documento define cómo el sistema expande sus capacidades mediante herramientas externas, priorizando la seguridad y el aislamiento de credenciales.

## 🏗️ Arquitectura Híbrida

El sistema utiliza dos patrones de transporte para comunicarse con servidores MCP:

### 1. Servidores Locales (Transporte: STDIO)
*   **Definición**: El proceso es lanzado directamente por el CLI de Gemini como un proceso hijo.
*   **Casos de Uso**: Herramientas que interactúan con el sistema de archivos local o APIs que no manejan secretos críticos.
*   **Ejemplo**: `mcp-server-xubio`.
*   **Aislamiento**: Corre dentro del contexto del sandbox de Gemini.

### 2. Servidores Remotos/Periféricos (Transporte: SSE/HTTP)
*   **Definición**: El servidor corre de forma independiente (fuera del host o en un contenedor separado) y expone sus herramientas mediante un bridge HTTP (Server-Sent Events).
*   **Casos de Uso**: Integraciones con plataformas de terceros (ej: WooCommerce).
*   **Seguridad**: 
    *   **Aislamiento de Secretos**: Las API Keys críticas residen exclusivamente en el servidor periférico. El CLI de Gemini nunca tiene acceso a ellas.
    *   **Resiliencia**: El servidor puede ser reiniciado o actualizado sin afectar la sesión de chat activa.

## 🔒 Directrices de Seguridad

1.  **Mínimo Privilegio**: Solo los servidores que requieren acceso al host deben usar STDIO.
2.  **Ofuscación de Credenciales**: Siempre que sea posible, preferir SSE para evitar que el modelo de IA pueda "ver" variables de entorno sensibles mediante comandos de sistema.
3.  **Configuración**: Las URLs de los servidores SSE se definen en el archivo de configuración del CLI, manteniendo el desacoplamiento total.

---
*Este documento es la única fuente de verdad para la estrategia MCP del proyecto.*
