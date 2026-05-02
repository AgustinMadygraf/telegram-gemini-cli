# Telegram Gemini CLI Bridge

Bridge asíncrono para vincular Telegram con Gemini CLI (MCP).

## Arquitectura

Implementación de **Clean Architecture (Hexagonal)**:
- **Entities**: Objetos de negocio.
- **Use Cases & Ports**: Lógica y contratos.
- **Interface Adapters**: Controllers, Gateways y Presenters.
- **Infrastructure**: FastAPI, Red y Configuración.

## Estructura del Código

```text
src/
├── entities/               # Lógica de negocio
├── use_cases/              # Reglas de aplicación
│   └── ports/              # Interfaces (Puertos)
├── interface_adapters/     # Adaptadores de interfaz
│   ├── controllers/        # FastAPI -> Use Case
│   ├── gateways/           # Impl. de Gemini y Telegram
│   └── presenters/         # Formateadores
└── infrastructure/         # Detalles técnicos
    ├── fastapi/            # Configuración de red
    └── setting/            # Configuración y Logging
```

## Ejecución

1. Configurar `.env` (ver `.env.example`).
2. Activar entorno: `source venv/bin/activate`.
3. Ejecutar: `python main.py`.
