# Discovery & Open Questions

## Certezas del Diseño

1. **Nomenclatura**: Se utiliza `src/use_cases/ports/` para las interfaces para evitar confusión con los adaptadores.
2. **Hard Exit**: El sistema no arranca si falla la validación de Gemini o Telegram.
3. **Encabezados de Seguridad**: Se utiliza un secreto compartido en el Header para validar el Webhook.

## Dudas Actuales

### 1. Validación de Salud del Webhook
- **Afirmación**: El sistema debe consultar `getWebhookInfo` al arrancar.
- **Duda**: ¿Debería el sistema intentar configurar el webhook automáticamente si detecta una discrepancia en la URL registrada en Telegram?

### 2. Detección de Proxy/Túnel
- **Afirmación**: Estamos corriendo detrás de Cloudflare Tunnel.
- **Duda**: ¿Necesitamos validar explícitamente que la IP de origen del Webhook pertenece al rango oficial de Telegram?

### 3. Persistencia de Sesión Gemini
- **Afirmación**: Usamos `--resume latest`.
- **Duda**: ¿Cómo manejar múltiples usuarios si Gemini CLI no soporta IDs de sesión separados por defecto en modo persistente simple?
