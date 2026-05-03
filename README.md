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

## 🏛️ Arquitectura del Sistema

El proyecto sigue los principios de **The Clean Architecture**:

1.  **Entities**: Objetos de dominio puros (`ChatMessage`, `AIResponse`).
2.  **Use Cases**: Lógica de aplicación (`ProcessMessage`, `SystemValidatorService`).
3.  **Interface Adapters**:
    *   **Gateways**: Gemini y Telegram.
    *   **Presenters**: Conversión de Markdown a HTML seguro para Telegram.
4.  **Infrastructure**: FastAPI, Shell, Logger, Settings.

---

## 🔒 Seguridad
*   **Validación de Webhook**: Uso de `secret_token` en el Header.
*   **Whitelisting**: Respuesta exclusiva a `ALLOWED_CHAT_IDS`.
*   **Graceful Shutdown**: Cierre limpio de procesos al recibir `CTRL+C`.

---
*Desarrollado con ❤️ para entornos Gemini avanzados.*
