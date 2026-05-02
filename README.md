# 🚀 Telegram Gemini Bridge (Clean Architecture & Multi-Auth)

Bridge de producción asíncrono que vincula Telegram con el ecosistema **Gemini CLI (MCP)** mediante una arquitectura ultra-robusta y extensible.

## ✨ Características Principales

*   **🛡️ Multi-Auth Strategy**: Soporta 3 vías de autenticación: `api_key` nativa, `google_auth` (herencia de identidad de usuario) y `vertex_ai`.
*   **🏗️ Clean Architecture & DDD**: Estructura desacoplada en capas (Entities, Use Cases, Adapters, Infrastructure).
*   **📂 Aislamiento de Sesiones**: Cada usuario de Telegram tiene un entorno Gemini independiente en `storage/sessions/`, garantizando privacidad y persistencia del contexto.
*   **🔍 Deep Health Check**: Validación obligatoria al arranque de binarios, DNS, túneles Cloudflare y salud del Webhook de Telegram.
*   **🚇 Gestión de Túnel Automática**: Integración con `cloudflared` y protección de puertos (`PortGuard`) para evitar conflictos de ejecución.
*   **🧪 Suite de Pruebas**: Cobertura del ~89% validando lógica de negocio, red e infraestructura.

---

## 🛠️ Requisitos de Infraestructura

### 1. Gemini CLI
Debes tener instalado el binario de Gemini. [Instrucciones oficiales aquí](https://github.com/google/gemini-cli).

### 2. Cloudflared (Túnel HTTPS)
Necesario para recibir los webhooks de Telegram de forma segura.
```bash
# Ubuntu/Debian
sudo apt-get install cloudflared
```

---

## ⚙️ Configuración

Copia el archivo `.env.example` a `.env` y completa las variables:

| Variable | Descripción |
| :--- | :--- |
| `GEMINI_AUTH_METHOD` | `api_key`, `google_auth` o `vertex_ai`. |
| `TELEGRAM_BOT_TOKEN` | Token obtenido de @BotFather. |
| `ALLOWED_CHAT_IDS` | Lista JSON de IDs permitidos (ej: `[123, 456]`). |
| `WEBHOOK_URL` | Tu dominio de Cloudflare (ej: `https://tu-tuna.trycloudflare.com`). |
| `CLOUDFLARE_TOKEN` | Token de tu túnel de Cloudflare. |

---

## 🚀 Ejecución y Mantenimiento

### Iniciar el Sistema
```bash
python main.py
```
*El sistema liberará automáticamente el puerto 8000, iniciará el túnel de Cloudflare y validará todas las credenciales antes de quedar online.*

### Ejecutar Pruebas y Cobertura
Para asegurar que todo el sistema de autenticación e infraestructura está operativo:
```bash
export PYTHONPATH=$PYTHONPATH:. && pytest --cov=src --cov-report=term-missing tests/
```

---

## 🏛️ Arquitectura del Sistema

El proyecto sigue los principios de **The Clean Architecture**:

1.  **Entities**: Objetos de dominio puros (`ChatMessage`, `AIResponse`).
2.  **Use Cases**: Lógica de aplicación (`ProcessMessage`, `SystemValidatorService`).
3.  **Interface Adapters**: Gateways para Gemini y Telegram, y controladores FastAPI.
4.  **Infrastructure**: Implementaciones de bajo nivel (Shell, PortGuard, Config).

### Estructura de Directorios
```text
.
├── src/
│   ├── entities/           # Reglas de negocio críticas
│   ├── use_cases/          # Orquestación de la aplicación
│   ├── interface_adapters/ # Gateways (Gemini, Telegram) y Presenters
│   └── infrastructure/     # FastAPI, Shell, Logger, Settings
├── storage/                # Persistencia (Sesiones, Logs, Temp)
├── tests/                  # Suite de pruebas Pytest
└── main.py                 # Punto de entrada y Lifespan
```

---

## 🔒 Seguridad
*   **Validación de Webhook**: Se utiliza un `secret_token` único en el Header de Telegram para evitar peticiones malintencionadas.
*   **Whitelisting**: El bot solo responde a los IDs de usuario definidos en `ALLOWED_CHAT_IDS`.
*   **Graceful Shutdown**: El sistema cierra todos los túneles y procesos hijos al recibir `CTRL+C`.

---
*Desarrollado con ❤️ para entornos Gemini avanzados.*
