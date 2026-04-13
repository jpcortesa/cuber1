# Taller Sumativo – Despliegue de entorno con Docker

**Asignatura:** Aplicaciones y Tecnologías de la Web
**Universidad:** San Sebastián
**Estudiante:** Jorge Cortés A.
**Fecha:** 21/03/2026

---

## Descripción del entorno

Este proyecto despliega un entorno web de tres capas utilizando Docker y Docker Compose, siguiendo la arquitectura **cliente-servidor en contenedores**:

| Servicio   | Tecnología           | Puerto (host) | Puerto (contenedor) |
|------------|----------------------|:-------------:|:-------------------:|
| Frontend   | Nginx 1.25-alpine    | 8080          | 80                  |
| Backend    | Python 3.11 / Flask  | 3000          | 5000                |
| Base datos | PostgreSQL 16-alpine | 5432          | 5432                |

---

## Justificación de imágenes seleccionadas

### ¿Por qué imágenes `-alpine`?

Las variantes Alpine están basadas en Alpine Linux, una distribución minimalista de ~5 MB. Su uso en entornos de contenedores es una buena práctica reconocida en la industria porque:

- **Reduce la superficie de ataque**: menos paquetes instalados implican menos vulnerabilidades potenciales.
- **Acelera las transferencias**: imágenes más pequeñas se descargan y despliegan más rápido en CI/CD.
- **Ahorra espacio en disco y en registros de imágenes** (Docker Hub, AWS ECR, etc.).

### ¿Por qué no usar `latest`?

La etiqueta `latest` no garantiza reproducibilidad: lo que hoy es `latest` puede ser diferente en tres meses. Fijar versiones específicas (`nginx:1.25-alpine`, `postgres:16-alpine`, `python:3.11-slim`) asegura que el entorno sea **idéntico** en cualquier máquina y en cualquier momento, principio fundamental del desarrollo profesional.

### Detalle por servicio

**`nginx:1.25-alpine`** — Frontend
Imagen oficial de Nginx. La versión 1.25 es la rama estable actual con soporte activo. La variante alpine reduce el tamaño de ~140 MB (imagen estándar) a ~25 MB. Nginx es la opción estándar de la industria para servir aplicaciones web estáticas en contenedores.

**`python:3.11-slim`** — Backend
Imagen oficial de Python. La variante `slim` elimina compiladores y documentación de desarrollo, reduciendo el tamaño de ~900 MB a ~45 MB. Python 3.11 tiene soporte oficial hasta 2027 y ofrece mejoras de rendimiento respecto a versiones anteriores. Se eligió `slim` en lugar de `alpine` porque Flask con psycopg2 requiere algunas librerías C que `alpine` no incluye por defecto, lo que complicaría el Dockerfile sin beneficio significativo de tamaño.

**`postgres:16-alpine`** — Base de datos
Imagen oficial de PostgreSQL. La versión 16 es LTS con soporte hasta 2028. La variante alpine reduce el tamaño de ~400 MB a ~80 MB. PostgreSQL es el sistema de gestión de bases de datos relacional open source más robusto y utilizado en la industria.

---

## Estructura del proyecto

```
taller-docker/
├── docker-compose.yml        # Orquestación de los 3 servicios
├── README.md                 # Este archivo
├── reflexion.md              # Reflexión escrita del taller
├── frontend/
│   ├── Dockerfile            # Imagen Nginx para el frontend
│   ├── nginx.conf            # Configuración del servidor web
│   └── html/
│       └── index.html        # Interfaz web del proyecto
└── backend/
    ├── Dockerfile            # Imagen Python/Flask para el backend
    ├── requirements.txt      # Dependencias Python
    └── app.py                # API REST con endpoints
```

---

## Cómo ejecutar el entorno

### Requisitos previos

- Docker Desktop instalado y en ejecución
- Puerto 8080, 3000 y 5432 disponibles en el host

### Comandos

```bash
# 1. Clonar/descomprimir el proyecto y entrar a la carpeta
cd taller-docker

# 2. Construir las imágenes y levantar todos los contenedores
docker-compose up --build

# 3. Verificar que los contenedores estén corriendo
docker ps

# 4. Acceder a los servicios en el navegador
#    Frontend:  http://localhost:8080
#    Backend:   http://localhost:3000/status
#    Visitas:   http://localhost:3000/visitas

# 5. Ver los logs de un servicio específico
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 6. Detener el entorno (mantiene los datos del volumen)
docker-compose down

# 7. Detener y ELIMINAR el volumen de datos
docker-compose down -v
```

---

## Configuración de volúmenes y puertos

### Volúmenes

| Volumen         | Tipo    | Ruta en contenedor             | Propósito                                      |
|-----------------|---------|-------------------------------|------------------------------------------------|
| `postgres_data` | Nombrado| `/var/lib/postgresql/data`     | Persistencia de datos de PostgreSQL            |
| `./frontend/html` | Bind  | `/usr/share/nginx/html`        | Edición de HTML sin reconstruir la imagen      |

El volumen nombrado `postgres_data` es gestionado por Docker y **persiste aunque el contenedor sea eliminado**. Esto garantiza que los datos almacenados en la base de datos no se pierdan entre reinicios del entorno.

### Puertos

| Host  | Contenedor | Servicio  | Justificación                                             |
|:-----:|:----------:|-----------|----------------------------------------------------------|
| 8080  | 80         | Frontend  | Puerto 80 reservado en muchos sistemas; 8080 es estándar de desarrollo |
| 3000  | 5000       | Backend   | Flask usa 5000 por defecto; 3000 en host sigue convención Node.js/APIs |
| 5432  | 5432       | PostgreSQL| Puerto estándar de PostgreSQL, expuesto sólo para depuración |

---



