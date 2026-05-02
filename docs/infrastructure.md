# Gestión de Infraestructura y Red

Este proyecto incluye herramientas para gestionar el ciclo de vida de los procesos y asegurar que el bot esté siempre accesible.

## 🚇 Túneles Cloudflare (Automático)

El sistema integra `CloudflareTunnelRunner`, que se encarga de:
1.  Verificar si el binario `cloudflared` está presente.
2.  Levantar el túnel asíncronamente usando el `CLOUDFLARE_TOKEN` definido.
3.  Validar la propagación DNS: El bot no arranca el `deep_health_check` hasta que la `WEBHOOK_URL` resuelve correctamente a una dirección IP (verificación mediante `socket.gethostbyname`).

## 🛡️ PortGuard (Protección de Puerto)

Para evitar el error `OSError: [Errno 98] Address already in use`, se ha implementado el componente `PortGuard`.
*   **Acción**: Al arrancar, escanea el puerto 8000 (o el configurado). Si detecta un proceso intruso, ejecuta un `kill` limpio (SIGTERM) para liberar el recurso.
*   **Beneficio**: Permite reinicios rápidos del bot sin tener que buscar y matar procesos manualmente en la terminal.

## 📂 Sistema de Almacenamiento (`storage/`)

El directorio `storage/` es el único lugar donde el bot escribe datos en disco:
*   `storage/sessions/`: Subdirectorios por `chat_id` que contienen las bases de datos de Gemini CLI y sus contextos.
*   `storage/logs/`: Registros detallados del túnel de Cloudflare (`tunnel.log`) y de la aplicación.
*   `storage/temp/`: Archivos efímeros generados durante el procesamiento.

**Nota**: El archivo `.gitignore` está configurado para excluir esta carpeta, asegurando que los datos sensibles de los chats no se suban al repositorio.

---

## 🛠️ Deep Health Check

Al iniciar, el `SystemValidatorService` ejecuta una secuencia crítica:
1.  **Binario Gemini**: Comprueba que el CLI está instalado.
2.  **Auth Ping**: Realiza una consulta mínima (`gemini -p hi`) para verificar que las credenciales (API Key o Google Auth) son válidas. Si la IA responde "Unauthorized", el sistema se detiene.
3.  **Network Sync**: Consulta a Telegram el estado del Webhook. Si la URL configurada no coincide con la registrada en los servidores de Telegram, la sincroniza automáticamente.
