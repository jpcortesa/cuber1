# =============================================================
# Dockerfile – Servicio Frontend
# Imagen base: nginx:1.25-alpine
#
# Justificación de la imagen:
#   - "nginx" es la imagen oficial del servidor Nginx en Docker Hub.
#   - La variante "alpine" está basada en Alpine Linux (~5 MB base),
#     lo que reduce el tamaño total del contenedor a ~25 MB.
#   - Se fija la versión "1.25" (LTS) en lugar de "latest" para
#     garantizar reproducibilidad: el mismo Dockerfile producirá
#     exactamente el mismo entorno en cualquier máquina o fecha.
#   - No se necesitan dependencias adicionales: Nginx sólo sirve
#     archivos estáticos (HTML, CSS, JS).
# =============================================================

FROM nginx:1.25-alpine

# ── Metadatos del contenedor ──────────────────────────────
# Buena práctica: documentar quién mantiene la imagen y su propósito
LABEL maintainer="Jorge Cortés A."
LABEL description="Frontend del taller Docker - Aplicaciones y Tecnologías de la Web"
LABEL version="1.0"

# ── Copiar configuración personalizada de Nginx ───────────
# Reemplazamos la configuración por defecto por una ajustada
# al proyecto (proxy hacia el backend, cabeceras de seguridad).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ── Copiar archivos estáticos del frontend ────────────────
# Se copian los archivos HTML/CSS/JS al directorio raíz de Nginx.
# En el docker-compose también se monta un volumen sobre este
# directorio, lo que permite editar sin reconstruir la imagen.
COPY html/ /usr/share/nginx/html/

# ── Usuario no root ───────────────────────────────────────
# Nginx en alpine ya corre el worker process como usuario "nginx"
# (no root) de forma predeterminada en versiones recientes.
# El proceso master necesita root para enlazar el puerto 80;
# los workers usan el usuario sin privilegios "nginx".

# ── Puerto expuesto ───────────────────────────────────────
# Declaración informativa: el contenedor escucha en el puerto 80.
# El mapeo real al host (8080:80) se define en docker-compose.yml.
EXPOSE 80

# ── Comando de inicio ─────────────────────────────────────
# "-g daemon off;" mantiene Nginx en primer plano (foreground),
# necesario para que Docker detecte si el proceso termina.
CMD ["nginx", "-g", "daemon off;"]
