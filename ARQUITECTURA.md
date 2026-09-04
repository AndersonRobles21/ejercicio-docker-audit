# Arquitectura del proyecto

## Estado anterior

El proyecto arrancó como una app Flask chica con todo mezclado en un solo archivo. Tenía varios problemas prácticos:

- Credenciales de base de datos hardcodeadas en el código.
- SQL injection por concatenación de strings en el endpoint `/buscar`.
- Modo debug activo por defecto y binding a `0.0.0.0`.
- Health check deliberadamente inestable.
- Sin gestión de dependencias (`requirements.txt` no existía).
- Sin configuración por variables de entorno.
- Sin `.gitignore` ni `.dockerignore`.
- Dockerfile con imagen base obsoleta (`python:3.8`) y ejecución como root.
- No había Docker Compose, así que no se podía levantar el entorno completo con un solo comando.

## Estado actual

Se refactorizó el proyecto manteniendo la funcionalidad original, pero separando configuración de código, endureciendo la seguridad y agregando contenedores reproducibles.

### Cambios principales

- Credenciales movidas a variables de entorno.
- SQL injection corregido con validación de entrada y consulta parametrizada.
- Debug desactivado por defecto y controlado por `FLASK_DEBUG`.
- Health check estabilizado: siempre devuelve `200 OK` cuando el servicio responde.
- Manejo de errores mejorado: no se exponen excepciones ni detalles internos al cliente. Los errores se loguean.
- Dependencias declaradas en `requirements.txt` con versiones fijas y compatibles.
- Dockerfile actualizado a `python:3.12-slim` con usuario no root.
- Docker Compose agrega el servicio de API y base de datos para levantar el entorno completo localmente.

## Estructura

```
ejercicio-docker-audit/
├── app.py
├── test_app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
├── bandit_auditoria.txt
└── AUDITORIA.md
```

## Dependencias

`requirements.txt` declara las dependencias con versiones fijas:

- `Flask==2.3.3`
- `PyMySQL==1.1.1`
- `cryptography==50.0.1` (necesario para autenticación MySQL 8.0)
- `pytest==7.4.3`

No hay dependencias innecesarias. Se evitó mantener versiones extremadamente antiguas sin razón.

## Configuración

Las variables de entorno se definen en `.env` (no versionado) y `.env.example` (documentación).

Variables utilizadas:

- `FLASK_DEBUG`: activa o desactiva el modo debug de Flask.
- `FLASK_HOST`: interfaz de red donde escucha la app.
- `DB_HOST`: host de la base de datos.
- `DB_USER`: usuario de la base de datos.
- `DB_PASS`: contraseña de la base de datos.
- `DB_NAME`: nombre de la base de datos.

En Docker Compose, `FLASK_HOST` y `DB_HOST` se sobrescriben para que la API se comunique correctamente con el contenedor de base de datos.

## Docker

### Dockerfile

- Imagen base: `python:3.12-slim`.
- Instala dependencias desde `requirements.txt`.
- Copia el código y crea un usuario no root (`appuser`).
- Expone el puerto `5050`.
- Inicia la app con `python app.py`.

### .dockerignore

Excluye archivos innecesarios del contexto de build: `.venv`, `.git`, `__pycache__`, `.pytest_cache`, `.env`, artefactos de Python y documentos de auditoría.

### docker-compose.yml

Servicios:

- `api`: construye la imagen local, expone el puerto `5050`, carga variables de entorno desde `.env`, depende de `db`.
- `db`: imagen `mysql:8.0`, configura base de datos y usuario desde variables de entorno, usa volumen `db_data` para persistencia y healthcheck para verificar disponibilidad.

Red interna `app-network` para comunicación entre contenedores.

## Seguridad

Correcciones realizadas:

- **Secretos:** se eliminaron credenciales hardcodeadas. Ahora se cargan desde variables de entorno.
- **SQL injection:** el endpoint `/buscar` valida que el parámetro `id` sea numérico y usa placeholder `%s` en la consulta simulada.
- **Manejo de errores:** el endpoint `/` no devuelve tracebacks ni detalles de conexión al cliente. Los errores se registran en logs.
- **Debug:** `debug=True` fue reemplazado por una variable de entorno. Por defecto está desactivado.
- **Binding de red:** el host de escucha es configurable. Por defecto usa `127.0.0.1` en desarrollo; en Docker Compose se fuerza `0.0.0.0` solo para el contenedor.
- **Usuario en contenedor:** el Dockerfile crea y usa `appuser` en lugar de ejecutar como root.
- **Trivy:** se ejecutó análisis de imagen. El CVE crítico de PyMySQL fue solucionado actualizando a `1.1.1`.

## Próximo paso

Los siguientes pasos recomendados están fuera del alcance de esta refactorización:

- GitHub Actions para CI/CD.
- Despliegue en AWS/EC2.
- Nginx, HTTPS y DNS.
- Dozzle y Uptime Kuma.
