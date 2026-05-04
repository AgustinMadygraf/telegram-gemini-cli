# Model Context Protocol (MCP) Integration Strategy

Este documento define cómo el sistema expande sus capacidades mediante herramientas externas, priorizando la seguridad y el aislamiento de credenciales.

## 📍 Configuración Actual

### Fuente de verdad: `~/.gemini/settings.json`

Los servidores MCP están definidos **exclusivamente** en el archivo de configuración global de Gemini CLI (`~/.gemini/settings.json`), en la sección `mcpServers`. **No existe ninguna variable en `.env`** que declare qué MCPs usa este proyecto.

Esto implica:
*   La configuración es **local a la máquina**, no portable entre entornos.
*   El `.env` no documenta qué servidores MCP son necesarios para operar.
*   Un nuevo despliegue requiere configurar `~/.gemini/settings.json` manualmente.

### Flujo actual de integración

```
~/.gemini/settings.json (fuente)
        │
        ├─► GeminiLocalConfigAdapter.get_include_directories()
        │       → Extrae directorios de scripts MCP
        │       → Genera flags --include-directories para el CLI
        │
        ├─► CredentialSyncService.sync_credentials()
        │       → Copia settings.json a la sesión aislada
        │       → Sanea servidores con paths inválidos
        │
        └─► MCPValidatorAdapter.validate()
                → Verifica existencia física de scripts
                → Reporta estado en el Deep Health Check
```

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

## ⚠️ Sandbox vs Include-Directories

Existe una incompatibilidad entre `--sandbox` y `--include-directories`:

| Modo | Comportamiento | MCPs |
|---|---|---|
| `--sandbox` | Filesystem aislado, confianza implícita | ❌ No puede acceder a directorios externos de MCPs |
| Sin sandbox + `--include-directories` + `--skip-trust` | Filesystem real, confianza explícita | ✅ Acceso a directorios de MCPs |

El sistema selecciona automáticamente el modo según la presencia de MCPs configurados.

## 🔒 Directrices de Seguridad

1.  **Mínimo Privilegio**: Solo los servidores que requieren acceso al host deben usar STDIO.
2.  **Ofuscación de Credenciales**: Siempre que sea posible, preferir SSE para evitar que el modelo de IA pueda "ver" variables de entorno sensibles mediante comandos de sistema.
3.  **Configuración**: Las URLs de los servidores SSE se definen en el archivo de configuración del CLI, manteniendo el desacoplamiento total.

## 🔄 Ciclo de Vida y Verificación

Para garantizar la estabilidad operativa (Observabilidad), el sistema implementa una fase de validación obligatoria al arranque:

1.  **Descubrimiento**: El `SystemValidatorService` lee la configuración de servidores MCP activos.
2.  **Verificación de Salud (Health Check)**:
    *   **STDIO**: Se comprueba la existencia física de los archivos ejecutables o scripts definidos.
    *   **SSE/HTTP**: Se realiza un "ping" de red al endpoint para confirmar disponibilidad.
3.  **Falla Visible**: Si un servidor no está disponible, el sistema genera un **Reporte de Acción**:
    *   En lugar de una instalación automática (que podría comprometer la estabilidad), el bot imprime en consola la instrucción exacta para corregir el fallo (ej: `npm install` o verificar URL).

---
*Este documento es la única fuente de verdad para la estrategia MCP del proyecto.*
