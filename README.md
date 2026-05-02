# Telegram Gemini CLI Bridge

Bridge asíncrono para vincular Telegram con Gemini CLI (MCP).

## Arquitectura

Implementación de **Clean Architecture (Hexagonal)** al más alto nivel:
- **Zero-Dep Adapters**: Los adaptadores no dependen de librerías externas ni del OS.
- **Deep Health Check**: Validación obligatoria de credenciales, red y túneles en el arranque.
- **Inversión de Control**: Todo el sistema se configura mediante inyección de dependencias en el arranque.

## Estructura del Código

```text
src/
├── entities/               # Lógica de negocio (Entidades puras)
├── use_cases/              # Reglas de aplicación
│   └── ports/              # Interfaces (Contratos de sistema y negocio)
├── interface_adapters/     # Adaptadores de interfaz (Silent Gateways)
│   ├── controllers/        # Controladores agnósticos
│   ├── gateways/           # Implementaciones de puertos
│   └── presenters/         # Formateadores (Capa de presentación)
└── infrastructure/         # Detalles técnicos y Frameworks
    ├── fastapi/            # Configuración de red y Web
    ├── shell/              # Bajo nivel (Asyncio, OS)
    └── setting/            # Configuración y Logging
```

## Ejecución

1. Configurar `.env` incluyendo `WEBHOOK_URL` y `CLOUDFLARE_TOKEN`.
2. Activar entorno: `source venv/bin/activate`.
3. Ejecutar: `python main.py`.
