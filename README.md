# Telegram Gemini CLI Bridge

Bridge asíncrono para vincular Telegram con Gemini CLI (MCP).

## Arquitectura

Implementación de **Clean Architecture (Hexagonal)**:
- **Ports & Adapters**: Desacoplamiento total de Gemini, Telegram y Cloudflare.
- **Deep Health Check**: Validación obligatoria de credenciales y red en el arranque.

## Estructura del Código

```text
src/
├── entities/               # Lógica de negocio
├── use_cases/              # Reglas de aplicación
│   └── ports/              # Interfaces (Puertos)
├── interface_adapters/     # Adaptadores de interfaz
│   ├── controllers/        # Controladores FastAPI
│   ├── gateways/           # Impl. de Gemini, Telegram y Cloudflare
│   └── presenters/         # Formateadores de salida
└── infrastructure/         # Detalles técnicos
    ├── fastapi/            # Server setup
    └── setting/            # Configuración y Logging
```

## Ejecución

1. Configurar `.env` incluyendo `WEBHOOK_URL` y `CLOUDFLARE_TOKEN`.
2. Activar entorno: `source venv/bin/activate`.
3. Ejecutar: `python main.py`.
