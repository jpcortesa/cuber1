"""
================================================
Taller Sumativo – Despliegue de entorno con Docker
Servicio: Backend API REST
Curso: Aplicaciones y Tecnologías de la Web
Universidad San Sebastián
================================================
"""

# ── Importaciones ──────────────────────────────────────────
import os          # Para leer variables de entorno (credenciales de BD)
import psycopg2    # Conector para PostgreSQL
from flask import Flask, jsonify
from flask_cors import CORS  # Permite peticiones desde el frontend (diferente origen)

# ── Configuración de la aplicación ────────────────────────
app = Flask(__name__)
CORS(app)  # Habilita CORS para todos los endpoints

# ── Configuración de la base de datos ─────────────────────
# Las credenciales se leen desde variables de entorno (definidas
# en docker-compose.yml). NUNCA se hardcodean en el código fuente.
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     os.environ.get("DB_PORT", 5432),
    "dbname":   os.environ.get("DB_NAME", "tallerdb"),
    "user":     os.environ.get("DB_USER", "talleruser"),
    "password": os.environ.get("DB_PASSWORD", "tallerpass"),
}


def obtener_conexion_bd():
    """
    Establece y retorna una conexión a PostgreSQL.

    Retorna:
        psycopg2.connection: objeto de conexión activa a la BD.
    Lanza:
        psycopg2.OperationalError si la BD no está disponible.
    """
    return psycopg2.connect(**DB_CONFIG)


def inicializar_bd():
    """
    Crea la tabla 'visitas' si no existe.
    Se ejecuta una sola vez al arrancar la aplicación.
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitas (
                id        SERIAL PRIMARY KEY,
                ruta      VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("[OK] Tabla 'visitas' lista en PostgreSQL.")
    except Exception as e:
        # En desarrollo se muestra el error; en producción se registraría en logs
        print(f"[WARN] No se pudo inicializar la BD: {e}")


# ── Endpoints de la API ────────────────────────────────────

@app.route("/status")
def estado_api():
    """
    GET /status
    Retorna el estado general de la API y verifica la conexión con la BD.
    Útil para healthchecks y demostración del entorno.
    """
    estado_bd = "desconectada"
    try:
        conn = obtener_conexion_bd()
        conn.close()
        estado_bd = "conectada"
    except Exception:
        pass

    return jsonify({
        "servicio":    "backend-flask",
        "estado":      "activo",
        "base_datos":  estado_bd,
        "puerto":      5000,
        "tecnologia":  "Python 3.11 + Flask 3.0"
    })


@app.route("/visitas", methods=["GET"])
def listar_visitas():
    """
    GET /visitas
    Retorna las últimas 10 visitas registradas en la BD.
    Demuestra la persistencia de datos con el volumen de PostgreSQL.
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()

        # Registrar esta visita en la BD
        cursor.execute("INSERT INTO visitas (ruta) VALUES ('/visitas');")

        # Obtener las últimas 10 visitas
        cursor.execute("""
            SELECT id, ruta, timestamp
            FROM visitas
            ORDER BY timestamp DESC
            LIMIT 10;
        """)
        filas = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        visitas = [
            {"id": f[0], "ruta": f[1], "timestamp": str(f[2])}
            for f in filas
        ]
        return jsonify({"total": len(visitas), "visitas": visitas})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Punto de entrada ───────────────────────────────────────

if __name__ == "__main__":
    inicializar_bd()
    # host="0.0.0.0" permite conexiones desde fuera del contenedor
    app.run(host="0.0.0.0", port=5000, debug=False)
