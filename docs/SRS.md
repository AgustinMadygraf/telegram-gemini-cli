# Software Requirements Specification (SRS) - Telegram Gemini CLI Bridge

## 1. Introducción
El sistema "Telegram Gemini CLI Bridge" actúa como un intermediario entre la API de Telegram y el ejecutable local `gemini-cli`. Su diseño se basa en **Clean Architecture**, **SOLID** y **Domain-Driven Design (DDD)**.

## 2. Certezas Técnicas (Technical Certainties)

1. **Lenguaje**: Python 3.10+.
2. **Framework Web**: FastAPI (Uvicorn como servidor ASGI).
3. **Comunicación**: Webhook de Telegram (HTTPS).
4. **Infraestructura de Túnel**: Cloudflare Tunnel (`cloudflared`) para exposición segura del entorno local.
5. **Backend AI**: `gemini-cli` vía subprocesos de Python (`subprocess`).
6. **Persistencia**: Flag `--resume latest` en Gemini.

## 3. Arquitectura Limpia (Clean Architecture)

### Capa de Dominio (Domain)
- **Entidades**: `Message`, `ChatSession`.
- **Value Objects**: `TelegramUserId`, `PromptResponse`.
- **Interfaces**: `AIEngineInterface`, `MessagingProviderInterface`.

### Capa de Aplicación (Use Cases)
- `HandleTelegramWebhook`: Orquestador que recibe el evento, valida al usuario y dispara la ejecución en Gemini.
- `ResetSession`: Comando para limpiar el historial de la sesión.

### Capa de Infraestructura (Infrastructure)
- **FastAPIAdapter**: Punto de entrada del Webhook.
- **GeminiCLIAdapter**: Wrapper de `subprocess.run(["gemini", ...])`.
- **CloudflareTunnel**: Configuración externa que redirige el tráfico HTTPS al puerto local de FastAPI.

## 4. Diseño del Sistema (Webhook Flow)

1. **Telegram API** -> [POST Webhook] -> **Cloudflare Edge**.
2. **Cloudflare Edge** -> [Encrypted Tunnel] -> **Local cloudflared daemon**.
3. **local cloudflared** -> [Proxy] -> **FastAPI (localhost:8000)**.
4. **FastAPI** -> [Process] -> **Gemini CLI**.
5. **Gemini CLI** -> [Response] -> **FastAPI** -> **Telegram API**.

## 5. Principios SOLID Aplicados

- **Dependency Inversion**: El caso de uso no conoce a FastAPI ni a `cloudflared`. Solo conoce la interfaz que recibe un mensaje.
- **Single Responsibility**: El adaptador de Gemini se encarga exclusivamente de parsear el stdout/stderr de la CLI.
