# Software Requirements Specification (SRS) - Telegram Gemini CLI Bridge

## 1. Introducción
El sistema "Telegram Gemini CLI Bridge" es un intermediario entre Telegram y `gemini-cli`, diseñado bajo una arquitectura de **Círculos Concéntricos (Clean Architecture / Hexagonal)** con abstracción total de dependencias de bajo nivel.

## 2. Certezas Técnicas
- **Stack**: Python, FastAPI, Cloudflare Tunnel.
- **Seguridad**: Whitelist de usuarios, validación de secretos de Webhook y **Hard Exit**.
- **Independencia del OS**: El núcleo no depende de `asyncio` o `os` directamente, sino de gateways de sistema.
- **Observabilidad Pasiva**: El sistema utiliza un `ValidationReport` para auditoría inicial y un **Middleware de Red** para auditoría operacional.

## 3. Capas de la Aplicación (Funcional)

### Capa 1: Dominio (Entities)
Define los objetos de negocio puros: Mensajes de Chat, Respuestas de IA, Reportes de Validación y Modelos de Red.

### Capa 2: Aplicación (Use Cases)
Define la lógica orquestadora: Procesamiento de mensajes, Validación de Salud del Sistema y Gestión de Sesiones. Utiliza **Ports** (interfaces) para comunicarse con el exterior sin conocer implementaciones técnicas.

### Capa 3: Adaptadores (Interface Adapters)
Traduce datos entre el dominio y las plataformas externas. Contiene Controladores de entrada, Presentadores de salida y Gateways de comunicación (Telegram, Gemini, Cloudflare).

### Capa 4: Infraestructura
Implementaciones concretas de bajo nivel: Servidor FastAPI, Ejecución de Shell asíncrona, Sistema de Archivos y Logger.

## 4. Validación de Salud (Deep Health Check)
El sistema valida secuencialmente antes del arranque:
1. **Credenciales**: Token de Bot y Binario de Gemini.
2. **Sistema**: Disponibilidad de binarios y permisos de archivos vía `FileSystemGateway`.
3. **Túnel**: Verificación de estado del túnel de Cloudflare.
4. **Red**: Sincronización automática de URL de Webhook en Telegram.
5. **Ecosistema MCP**: Verificación de disponibilidad de servidores STDIO y conectividad de servidores SSE antes de aceptar mensajes.
