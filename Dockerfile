
FROM docker:24-dind

WORKDIR /app

# Instala docker-compose
RUN apk add --no-cache docker-compose py3-pip

# Copia tu código
COPY docker-compose.yml .
COPY frontend/ ./frontend/
COPY backend/ ./backend/

# El comando que Fly ejecutará
CMD ["docker-compose", "up"]
