# Dockerfile (en la raíz)
FROM docker:24-dind

WORKDIR /app

# Instala docker-compose
RUN apk add --no-cache docker-compose

# Copia toda la configuración
COPY docker-compose.yml .
COPY frontend/ ./frontend/
COPY backend/ ./backend/

# Variables de entorno para producción
ENV FLASK_ENV=production
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=${DB_PASSWORD:-defaultpass}
ENV POSTGRES_DB=taller_db

# Expone los puertos
EXPOSE 80 3000 5432

# Comando de inicio
CMD ["docker-compose", "up"]
