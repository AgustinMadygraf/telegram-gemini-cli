# Discovery & Open Questions

## Certezas del Diseño

1. **Auto-registro**: El sistema sincroniza automáticamente la URL del webhook en Telegram si detecta una discrepancia.
2. **Ports/Interfaces**: La carpeta `src/use_cases/ports/` centraliza los contratos de infraestructura.
3. **Validación Triple**: El arranque valida IA, Mensajería y Túnel.

## Dudas Actuales

### 1. Gestión de Cloudflare Tunnel
- **Afirmación**: Usaremos `CLOUDFLARE_TOKEN` para validar el estado del túnel vía API.
- **Duda**: ¿Debería el sistema intentar lanzar el proceso `cloudflared` localmente o solo monitorear su estado externo?

### 2. Formateo de Respuesta (Presenter)
- **Afirmación**: El formateo de MarkdownV2 es complejo y requiere escapar caracteres específicos.
- **Duda**: ¿Cómo manejar la inyección de estilos (negritas, código) si Gemini devuelve texto plano o Markdown estándar?

### 3. Seguridad de Red
- **Afirmación**: Usamos un `secret_token` para validar el origen del webhook.
- **Duda**: ¿Es necesario implementar un rate-limiting a nivel de aplicación o delegamos esto a Cloudflare?
