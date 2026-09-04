# Auditoría técnica y de seguridad

## Resumen ejecutivo

- **Fecha:** 2026-09-04
- **Repo:** `/home/anderson/Documentos/ejercicioDocker/ejercicio-docker-audit`
- **Rama:** `main`
- **Entorno:** Linux local
- **Python:** 3.14.7
- **pytest:** 9.1.1
- **Bandit:** 1.9.4

Números rápidos:
- Pruebas encontradas: 1
- Pruebas ejecutadas: 0
- Errores de colección: 1
- Hallazgos totales: 13
- Altos: 2
- Medios: 4
- Bajos: 7

---

## Inspección inicial

El proyecto es chico: tiene `app.py`, `test_app.py` y un `Dockerfile`. No hay `requirements.txt`, `pyproject.toml`, `.gitignore`, `.env` ni config de pytest.

Es una app Flask 1.1.2 con PyMySQL 0.9.3, tres rutas (`/`, `/buscar`, `/health`) y un solo test para `/health`.

---

## Resultado de pruebas

```bash
.venv/bin/python -m pytest -v
```

**Resultado:** no se ejecutó ninguna prueba. Falló en la colección por incompatibilidad entre Flask 1.1.2 / Werkzeug 1.0.1 y Python 3.14.7 (`ast.Str` fue eliminado en Python 3.12).

- Pruebas encontradas: 1
- Pruebas ejecutadas: 0
- Aprobadas: 0
- Fallidas: 0
- Errores: 1
- Duración: 0.52s

---

## Análisis de seguridad con Bandit

```bash
.venv/bin/python -m bandit -r . -x ./.venv,./venv,./node_modules -f txt > bandit_auditoria.txt
```

- **Versión:** Bandit 1.9.4
- **Archivos analizados:** `app.py`, `test_app.py`
- **Hallazgos automáticos:** 6
  - Alta: 1
  - Media: 2
  - Baja: 3

| ID | Archivo | Línea | Hallazgo | Severidad | Confianza | Estado |
|----|---------|------:|----------|-----------|-----------|--------|
| BANDIT-01 | `app.py` | 10 | Contraseña hardcodeada (B105) | Baja | Media | Pendiente |
| BANDIT-02 | `app.py` | 25 | SQL injection por concatenación (B608) | Media | Baja | Pendiente |
| BANDIT-03 | `app.py` | 30 | Uso de `random.random` (B311) | Baja | Alta | Pendiente |
| BANDIT-04 | `app.py` | 35 | `debug=True` en Flask (B201) | Alta | Media | Pendiente |
| BANDIT-05 | `app.py` | 35 | Binding a `0.0.0.0` (B104) | Media | Media | Pendiente |
| BANDIT-06 | `test_app.py` | 7 | Uso de `assert` en tests (B101) | Baja | Alta | Pendiente |

---

## Hallazgos de revisión manual

### 1. Credenciales de BD en texto plano
En `app.py` líneas 8-11 hay credenciales escritas directamente. El historial de Git también las expone desde el primer commit. Riesgo: acceso no autorizado a la base de datos. Recomendación: mover a variables de entorno o gestor de secretos y rotar la contraseña.

### 2. Excepción cruda en respuesta HTTP
El endpoint `/` devuelve el mensaje de error completo al cliente. Riesgo: filtra información interna. Recomendación: devolver mensajes genéricos y loguear el error real.

### 3. Health check inestable
`/health` falla intencionalmente el 30% de las veces. Riesgo: falsos negativos en monitoreo y orquestadores. Recomendación: eliminar la aleatoriedad y reflejar el estado real de la app.

### 4. Cobertura de pruebas insuficiente
Solo hay una prueba para `/health`, y es inestable. No hay pruebas para `/` ni `/buscar`. Riesgo: regresiones sin detección. Recomendación: agregar tests para los endpoints faltantes y estabilizar el existente.

### 5. Incompatibilidad Dockerfile / entorno
El `Dockerfile` usa `python:3.8` y Flask 1.1.2, pero el entorno es Python 3.14.7. Riesgo: imagen potencialmente no ejecutable. Recomendación: actualizar imagen base y dependencias.

### 6. Ausencia de configuración básica
No hay `.gitignore`, `requirements.txt`, `pyproject.toml` ni configuración de pytest. Riesgo: commits accidentales de secretos o artefactos, entorno no reproducible. Recomendación: agregar estos archivos.

---

## Dependencias y Docker

### Dependencias

| Dependencia | En Dockerfile | En `.venv` | Observación |
|-------------|---------------|------------|-------------|
| Python | 3.8 | 3.14.7 | Incompatibilidad |
| Flask | 1.1.2 | 1.1.2 | No funciona limpio en Python 3.14 |
| PyMySQL | 0.9.3 | 0.9.3 | OK |
| Werkzeug | No declarado | 1.0.1 | Instalado para compatibilidad |
| Jinja2 | No declarado | 3.0.3 | Instalado para compatibilidad |
| itsdangerous | No declarado | 1.1.0 | Instalado para compatibilidad |

No existe `requirements.txt`. Las dependencias están solo en el Dockerfile, y varias transitivas no están declaradas en ningún lado.

### Dockerfile

```dockerfile
FROM python:3.8
WORKDIR /app
COPY . /app
RUN pip install Flask==1.1.2 PyMySQL==0.9.3
EXPOSE 5050
CMD ["python", app.py"]
```

Problemas principales:
- Imagen base obsoleta (Python 3.8 EOL).
- Ejecuta como root.
- Copia todo el directorio, incluyendo `.venv` y `__pycache__`.
- Sin `requirements.txt` separado.
- Sin usuario no root.
- Sin healthcheck.

---

## Conclusiones

El proyecto está en una etapa inicial con deuda técnica alta. Los problemas más importantes son:

1. Credenciales hardcodeadas y expuestas en Git.
2. Modo debug activo y binding a `0.0.0.0`.
3. SQL injection en `/buscar`.
4. Pruebas que no se pueden ejecutar por incompatibilidad de versiones.
5. Falta de configuración básica del proyecto.

Prioridades:
1. Rotar credenciales y extraerlas del código.
2. Desactivar `debug=True` y limitar el binding.
3. Corregir la inyección SQL.
4.Resolver la incompatibilidad de dependencias.
5. Estabilizar el health check y ampliar tests.
6. Crear `requirements.txt`, `.gitignore` y config de pytest.
7. Actualizar el Dockerfile.


