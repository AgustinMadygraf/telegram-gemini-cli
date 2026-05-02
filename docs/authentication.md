# Estrategias de Autenticación

El sistema es agnóstico a la forma en que te autenticas con Google Gemini, permitiendo alternar entre entornos personales y empresariales.

## 1. `api_key`
La forma más sencilla. Utiliza una API Key generada en [Google AI Studio](https://aistudio.google.com/).

*   **Configuración**: `GEMINI_AUTH_METHOD=api_key` y `GEMINI_API_KEY=tu_key`.
*   **Ideal para**: Prototipado rápido y uso personal básico.

## 2. `google_auth` (Herencia de Identidad)
Esta estrategia es la más avanzada y única de este proyecto. Permite al bot "heredar" las credenciales que ya tienes configuradas en tu máquina local.

*   **Funcionamiento**: El adaptador busca el directorio `~/.gemini` (donde Gemini CLI guarda el OAuth y las configuraciones de proyecto). Al iniciar una conversación, clona recursivamente esta configuración (excluyendo temporales y logs) al directorio aislado de la sesión en `storage/sessions/`.
*   **Configuración**: `GEMINI_AUTH_METHOD=google_auth`. No requiere llaves adicionales en el `.env`.
*   **Ideal para**: Usuarios que ya ejecutan `gemini` en su consola y quieren que el bot actúe exactamente como ellos (mismos proyectos, mismos permisos).

## 3. `vertex_ai` (Enterprise)
Para uso profesional en Google Cloud Platform.

*   **Configuración**:
    *   `GEMINI_AUTH_METHOD=vertex_ai`
    *   `VERTEX_PROJECT_ID=id-de-tu-proyecto`
    *   `VERTEX_LOCATION=us-central1` (o tu región)
*   **Ideal para**: Despliegues en servidores de GCP y entornos corporativos con cuotas escalables.

---

## Aislamiento de Entorno

Independientemente de la estrategia elegida, cada chat de Telegram tiene su propio **HOME** definido. El adaptador inyecta la variable de entorno `GEMINI_CLI_HOME` apuntando a `storage/sessions/chat_<id>`. Esto garantiza que:
1.  El historial de chat no se mezcle entre usuarios.
2.  Los archivos temporales y configuraciones de sesión sean efímeros y borrables de forma independiente.
