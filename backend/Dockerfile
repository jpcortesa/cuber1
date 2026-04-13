# =============================================================
# Dockerfile – Servicio Backend
# Imagen base: python:3.11-slim
#
# Justificación de la imagen:
#   - "python" es la imagen oficial de Python en Docker Hub.
#   - La variante "slim" elimina herramientas de compilación y
#     documentación innecesarias en producción (~45 MB vs ~900 MB).
#   - Se fija la versión "3.11" (estable, soporte hasta 2027) en
#     lugar de "latest" para garantizar reproducibilidad.
#   - Flask y psycopg2-binary no requieren compilación C adicional
#     en la variante slim, por lo que no se necesita "-bullseye"
#     ni la imagen completa.
# =============================================================

FROM python:3.11-slim

# ── Metadatos ─────────────────────────────────────────────
LABEL maintainer="Jorge Cortés A."
LABEL description="Backend API Flask del taller Docker - USS"
LABEL version="1.0"

# ── Variables de entorno del sistema ─────────────────────
# PYTHONDONTWRITEBYTECODE: evita crear archivos .pyc (innecesarios en contenedor)
# PYTHONUNBUFFERED: muestra los logs de Python en tiempo real (stdout/stderr)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── Directorio de trabajo dentro del contenedor ───────────
WORKDIR /app

# ── Instalación de dependencias ───────────────────────────
# Se copia primero sólo requirements.txt para aprovechar el
# caché de capas de Docker: si el código cambia pero las
# dependencias no, Docker no reinstala los paquetes.
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Copiar el código fuente ───────────────────────────────
COPY app.py .

# ── Crear usuario no root (buena práctica de seguridad) ──
# Correr procesos como root en un contenedor es un riesgo:
# si hay una vulnerabilidad en la app, el atacante tendría
# permisos de root dentro del contenedor.
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

USER appuser

# ── Puerto expuesto ───────────────────────────────────────
# Flask corre en el puerto 5000 dentro del contenedor.
# El mapeo al host (3000:5000) se define en docker-compose.yml.
EXPOSE 5000

# ── Comando de inicio ─────────────────────────────────────
# Se usa "python -m flask run" con host 0.0.0.0 para que Flask
# acepte conexiones desde fuera del contenedor (no sólo localhost).
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
