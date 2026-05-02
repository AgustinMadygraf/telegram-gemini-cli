# Telegram Gemini CLI Bridge

Este proyecto vincula un Bot de Telegram con `gemini-cli` utilizando un enfoque de **Arquitectura Limpia** y **DDD**.

## Tecnologías Principales

- **Lenguaje**: Python 3.10+
- **Framework API**: FastAPI
- **Túnel Seguro**: Cloudflare Tunnel
- **Motor AI**: Gemini CLI (backend local con soporte MCP)

## Estructura del Proyecto

```text
.
├── docs/
│   ├── SRS.md          # Requerimientos y Arquitectura
│   ├── DISCOVERY.md    # Dudas e Investigaciones
│   └── TODO.md         # Roadmap de tareas
├── src/                # (Pendiente) Código fuente
└── README.md
```

## Flujo de Trabajo
1. Telegram envía mensaje al Webhook expuesto por Cloudflare.
2. FastAPI procesa el mensaje y ejecuta `gemini-cli`.
3. Gemini interactúa con los servidores MCP (Xubio/WooCommerce).
4. La respuesta se envía de vuelta a Telegram de forma asíncrona.
