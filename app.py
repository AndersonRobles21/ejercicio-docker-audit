import logging
import os

import pymysql
from flask import Flask, request

app = Flask(__name__)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")


@app.route("/")
def home():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
        )
        conn.close()
        return "<h1>API Legacy TechNova - Funcionando</h1>"
    except Exception:
        logger.exception("Error al conectar a la base de datos")
        return "<h1>Sistema Caído</h1>", 500


@app.route("/buscar")
def buscar_usuario():
    usuario_id = request.args.get("id", "1")

    try:
        usuario_id_int = int(usuario_id)
    except (TypeError, ValueError):
        return "ID inválido", 400

    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id_int,))
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        if resultados:
            return f"<h1>Resultado de la busqueda</h1><p>{resultados}</p>"
        return "<h1>Usuario no encontrado</h1>", 404
    except Exception:
        logger.exception("Error al buscar usuario")
        return "<h1>Error al buscar usuario</h1>", 500


@app.route("/health")
def health_check():
    return "OK", 200


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    flask_host = os.getenv("FLASK_HOST", "127.0.0.1")
    app.run(host=flask_host, port=5050, debug=debug_mode)
