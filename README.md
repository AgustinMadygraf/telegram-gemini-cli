# Telegram Gemini CLI Bridge

Este proyecto permite vincular un Bot de Telegram con `gemini-cli`, habilitando el acceso remoto a las potentes capacidades de los servidores MCP (Model Context Protocol).

## Arquitectura y Diseño

Para garantizar un código robusto y profesional, el proyecto sigue los principios de:
- **Clean Architecture**: Separación estricta entre Dominio, Aplicación e Infraestructura.
- **SOLID**: Diseñado para el cambio y la testabilidad.
- **Domain-Driven Design (DDD)**: Centrado en el lenguaje del negocio (interacciones IA-Chat).

## Estructura de Documentación

- **[SRS.md](docs/SRS.md)**: Requerimientos, capas de arquitectura y principios SOLID aplicados.
- **[DISCOVERY.md](docs/DISCOVERY.md)**: Análisis técnico de dudas bajo la lente arquitectónica.
- **[TODO.md](docs/TODO.md)**: Roadmap de desarrollo organizado por capas de Clean Architecture.

## Tecnologías

- **Lenguaje**: Node.js / TypeScript.
- **Motor AI**: Gemini CLI (vía Shell Adapter).
- **Chat**: Telegram (vía Telegraf Adapter).
