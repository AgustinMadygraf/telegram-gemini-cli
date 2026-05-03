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
*   `storage/workspaces/`: Directorios de trabajo donde Gemini lee/edita archivos. Configurable mediante `GEMINI_WORKSPACE`.
*   `storage/logs/`: Registros detallados del túnel de Cloudflare (`tunnel.log`) y de la aplicación.
*   `storage/temp/`: Archivos efímeros generados durante el procesamiento.

**Nota**: El archivo `.gitignore` está configurado para excluir esta carpeta, asegurando que los datos sensibles de los chats no se suban al repositorio.

---

## 🛠️ Deep Health Check

Al iniciar, el `SystemValidatorService` ejecuta una secuencia crítica con reporte en tiempo real:
1.  **Binario Gemini**: Comprueba que el CLI está instalado.
2.  **Auth Ping**: Realiza una consulta mínima (`gemini -p hi`) para verificar que las credenciales son válidas.
3.  **Workspace Sync**: Si se define un `GEMINI_WORKSPACE`, el sistema asegura su existencia física.
4.  **Network Sync**: Sincroniza el Webhook con Telegram.

---

## 🌐 Estabilidad de Mensajería (HTML)

Para garantizar que el bot nunca falle al enviar una respuesta (problema común con MarkdownV2), el sistema utiliza:
*   **Librería `markdown`**: Convierte el formato de Gemini a HTML estándar.
*   **Whitelist Filtering**: Se eliminan etiquetas no soportadas por Telegram, manteniendo solo negritas, cursivas y bloques de código.
*   **Sanitización**: Se escapan automáticamente los caracteres reservados de HTML (`<`, `>`, `&`).
*   **Observabilidad de Fallos**: Ante errores `400 Bad Request` o fallos de la IA, el sistema loguea el payload íntegro.
*   **Fragmentación de Mensajes**: Si una respuesta o un error exceden los 4096 caracteres de Telegram, el sistema los divide automáticamente en múltiples mensajes para evitar el error `Message is too long`.

---

## 🛠️ Debugging y Testing desde la CLI

Si deseas probar el comportamiento del `gemini-cli` replicando exactamente lo que ve el bot (mismo historial y aislamiento), sigue estos pasos desde la terminal en la raíz del proyecto:

### 0. Activar Entorno Virtual
Antes de nada, asegúrate de estar en el entorno del proyecto:
```bash
source venv/bin/activate
```

### 1. Replicar el Entorno de Sesión
El bot utiliza la variable `GEMINI_CLI_HOME` para aislar cada chat. Para entrar en una sesión específica:
```bash
# Reemplaza <ID> por el ID del chat (ej: chat_1234567)
export GEMINI_CLI_HOME=storage/sessions/chat_<ID>
```

### 2. Ejecutar Consultas Manuales
Una vez exportada la variable, cualquier comando `gemini` que ejecutes usará esa base de datos de sesión:
```bash
# Para continuar la conversación del bot
gemini --resume -p "Hola, ¿qué dijimos antes?"

# Para ver la configuración de esa sesión específica
gemini --info
```

### 3. Verificar Credenciales
Si el bot usa una `GEMINI_API_KEY` del `.env`, también debes exportarla para que el CLI la reconozca:
```bash
export GEMINI_API_KEY="tu_llave_aqui"
```

### 4. Inspección de Archivos
Puedes ver físicamente los archivos de configuración y base de datos de esa sesión en:
`ls -la storage/sessions/chat_<ID>/.gemini/`
