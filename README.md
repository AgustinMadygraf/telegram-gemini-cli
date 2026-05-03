# 🚀 Telegram Gemini Bridge (Clean Architecture & Multi-Auth)

Bridge de producción asíncrono que vincula Telegram con el ecosistema **Gemini CLI (MCP)** mediante una arquitectura ultra-robusta y extensible.

## ✨ Características Principales

*   **🛡️ Multi-Auth Strategy**: Soporta 3 vías de autenticación: `api_key`, `google_auth` y `vertex_ai`.
*   **🏗️ Clean Architecture & DDD**: Estructura desacoplada en capas (Entities, Use Cases, Adapters, Infrastructure).
*   **🌐 Estabilidad HTML**: Conversión inteligente de Markdown a HTML (usando la librería `markdown`) para evitar errores de parseo en Telegram.
*   **📂 Aislamiento de Sesiones**: Entornos Gemini independientes por usuario en `storage/sessions/`.
*   **🔍 Deep Health Check**: Validación obligatoria al arranque de binarios, red y túneles.
*   **🚇 Gestión de Túnel Automática**: Integración con `cloudflared` y protección de puertos (`PortGuard`).
*   **🧪 Suite de Pruebas**: Cobertura del ~89% validando lógica de negocio e infraestructura.
*   **🧩 Hybrid MCP Architecture**: Integración de herramientas mediante Model Context Protocol, soportando ejecución local (STDIO) y remota (SSE/HTTP) para mayor seguridad.

---

## 🛠️ Requisitos de Infraestructura

### 1. Gemini CLI
[Instrucciones oficiales aquí](https://github.com/google/gemini-cli).

### 2. Cloudflared (Túnel HTTPS)
```bash
sudo apt-get install cloudflared
```

---

## ⚙️ Configuración

Copia `.env.example` a `.env` y completa las variables:

| Variable | Descripción |
| :--- | :--- |
| `GEMINI_AUTH_METHOD` | `api_key`, `google_auth` o `vertex_ai`. |
| `TELEGRAM_BOT_TOKEN` | Token de @BotFather. |
| `ALLOWED_CHAT_IDS` | Lista JSON de IDs permitidos. |
| `WEBHOOK_URL` | Dominio de Cloudflare. |
| `CLOUDFLARE_TOKEN` | Token de tu túnel. |

---

### Instalación y Preparación
```bash
# 1. Crear entorno virtual (si no existe)
python3 -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Iniciar el Sistema
```bash
# Asegúrate de que el venv esté activo
python main.py
```

### Ejecutar Pruebas y Cobertura
```bash
# Con el venv activo, simplemente:
pytest
```

---

## 🏛️ Arquitectura y Documentación

El sistema está diseñado bajo los principios de **Clean Architecture** y **DDD** para garantizar un desacoplamiento total.

*   [**Arquitectura**](docs/architecture.md): Capas del sistema, flujo de peticiones y observabilidad.
*   [**Infraestructura**](docs/infrastructure.md): Gestión de red, túneles, sandbox y almacenamiento.
*   [**Estrategia MCP**](docs/mcp.md): Integración híbrida de herramientas (STDIO y SSE/HTTP).
*   [**Autenticación**](docs/authentication.md): Detalles de `api_key`, `google_auth` y `vertex_ai`.
*   [**Requerimientos (SRS)**](docs/SRS.md): Especificación funcional del sistema.

---
*Desarrollado con ❤️ para entornos Gemini avanzados.*
