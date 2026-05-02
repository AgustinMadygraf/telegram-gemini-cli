# Telegram Gemini CLI Bridge

Bridge asíncrono para vincular Telegram con Gemini CLI (MCP), desarrollado con estándares de ingeniería de software de alto nivel.

## Arquitectura

Este proyecto implementa **Clean Architecture** de forma estricta:
- **Dependency Rule**: Las dependencias solo apuntan hacia el centro (Entidades -> Casos de Uso).
- **SOLID**: Desacoplamiento total entre frameworks (FastAPI/Telegram) y lógica de negocio.

## Estructura del Código

```text
src/
├── entities/               # Lógica de negocio (Entidades)
├── use_cases/              # Reglas de aplicación y Gateways (Interfaces)
├── interface_adapters/     # Adaptadores de interfaz
│   ├── controllers/        # Controladores de entrada (FastAPI)
│   ├── gateways/           # Implementación de Gateways
│   └── presenters/         # Formateadores de salida
└── infrastructure/         # Detalles técnicos
    ├── fastapi/            # Configuración de red y servidor
    ├── telegram/           # Configuración del bot
    └── setting/            # Configuración y Observabilidad
```

## Documentación Técnica

- **[SRS.md](docs/SRS.md)**: Detalle de capas y flujo de control.
- **[DISCOVERY.md](docs/DISCOVERY.md)**: Registro de decisiones y dudas técnicas.
- **[TODO.md](docs/TODO.md)**: Roadmap de refactorización y desarrollo.
