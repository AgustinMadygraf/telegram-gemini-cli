# Telegram Gemini CLI Bridge

Bridge asíncrono para vincular Telegram con Gemini CLI (MCP).

## Requisitos de Infraestructura

Para que el bot pueda recibir mensajes, es necesario un túnel HTTPS público (Cloudflare Tunnel).

### Instalación de cloudflared (Ubuntu)
```bash
sudo mkdir -p --mode=0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared/ jammy main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt-get update && sudo apt-get install cloudflared
```

## Arquitectura

Implementación de **Clean Architecture (Hexagonal)** al más alto nivel:
- **Zero-Dep Adapters**: Los adaptadores no dependen de librerías externas ni del OS.
- **Deep Health Check**: Validación obligatoria de credenciales, red y túneles en el arranque.
- **Inversión de Control**: Todo el sistema se configura mediante inyección de dependencias.

## Estructura del Código

```text
src/
├── entities/               # Lógica de negocio
├── use_cases/              # Reglas de aplicación
├── interface_adapters/     # Silent Gateways y Presenters
└── infrastructure/         # FastAPI, Shell y Middleware
```

## Ejecución

1. Configurar `.env` incluyendo `TELEGRAM_BOT_TOKEN`, `WEBHOOK_URL` y `CLOUDFLARE_TOKEN`.
2. Iniciar túnel: `cloudflared tunnel run --token <TU_TOKEN>`.
3. Ejecutar bot: `python main.py`.
