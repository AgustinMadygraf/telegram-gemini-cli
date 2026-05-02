# Discovery & Open Questions

## Certezas del Diseño

1. **Inversión de Dependencias**: Las interfaces (Gateways) vivirán en `src/use_cases/gateways/`.
2. **Presentación Asíncrona**: El uso de `BackgroundTasks` en FastAPI es obligatorio para cumplir con los tiempos de respuesta de Telegram.
3. **Hard Exit**: El sistema no debe arrancar si los componentes críticos (Gemini CLI, Telegram Token) fallan en la validación inicial.

## Dudas Actuales

### 1. Granularidad de los Presenters
- **Afirmación**: Los `Presenters` deben encargarse de escapar caracteres especiales para MarkdownV2, pero no deben saber nada del protocolo HTTP.
- **Duda**: ¿Cómo manejar el envío de fragmentos de mensajes largos de forma que el Use Case no se ensucie con la lógica de paginación de Telegram?

### 2. Inyección de Dependencias
- **Afirmación**: Necesitamos un orquestador central (main.py) que construya el grafo de dependencias.
- **Duda**: ¿Es conveniente usar un framework de DI (como `dependency_injector`) o mantenerlo manual para mantener la simplicidad inicial?

### 3. Persistencia de Configuración
- **Afirmación**: `pydantic-settings` es suficiente para la validación de entorno.
- **Duda**: ¿Deberíamos mover la whitelist de usuarios a un archivo `JSON` o base de datos pequeña si la lista crece más allá de unos pocos IDs?
