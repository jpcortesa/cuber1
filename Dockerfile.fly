FROM docker:latest

WORKDIR /app
COPY . .

RUN apk add --no-cache docker-compose

CMD ["docker-compose", "up"]
