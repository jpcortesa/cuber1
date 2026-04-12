# 🚀 GUÍA COMPLETA: DESPLIEGUE EN FLY.IO

## 📋 Arquitectura en Fly.io

Tu proyecto de 3 servicios se desplegará así en Fly.io:

```
tu-app-backend          → Flask API (Puerto 5000 → 80/443)
tu-app-frontend         → Nginx (Puerto 80 → 80/443)
PostgreSQL (Fly.io)     → Servicio gestionado por Fly.io
```

---

## 📦 Estructura de Carpetas

```
tu-repo/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── .dockerignore
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── html/
│       └── index.html
│
├── fly-backend.toml
├── fly-frontend.toml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔧 PASO 1: Instalación y Configuración Inicial

### 1.1 Instalar Fly.io CLI

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### 1.2 Autenticar con Fly.io

```bash
flyctl auth login
```

Abre el navegador, crea cuenta o inicia sesión. Regresa a terminal cuando termine.

### 1.3 Verificar instalación

```bash
flyctl version
flyctl auth whoami
```

---

## 📡 PASO 2: Crear PostgreSQL en Fly.io

### 2.1 Crear el servicio PostgreSQL

```bash
flyctl postgres create \
  --name taller-db \
  --region scl \
  --vm-size shared-cpu-1x \
  --initial-cluster-size 1
```

**Responde las preguntas:**
- `? App name`: taller-db (Enter)
- `? Select organization`: personal (Enter)
- `? Postgres password`: (deja vacío para auto-generar) (Enter)

### 2.2 Guarda las credenciales

El output mostrará algo como:
```
Connection string: 
postgres://talleruser:PASSWORD@taller-db.internal/tallerdb
```

**Copia y guarda esto en un lugar seguro.**

### 2.3 Obtener detalles de conexión

```bash
flyctl postgres connect -a taller-db
```

---

## 🖥️ PASO 3: Desplegar Backend (Flask)

### 3.1 Crear la app backend en Fly.io

```bash
flyctl apps create taller-docker-backend
```

O si ya existe:
```bash
flyctl launch --path . --name taller-docker-backend --no-deploy
```

### 3.2 Configurar variables de entorno

```bash
flyctl secrets set \
  --app taller-docker-backend \
  DATABASE_URL=postgres://talleruser:PASSWORD@taller-db.internal/tallerdb \
  FLASK_ENV=production
```

**Reemplaza `PASSWORD` con la contraseña real de PostgreSQL.**

### 3.3 Desplegar el backend

```bash
flyctl deploy \
  --config fly-backend.toml \
  --app taller-docker-backend
```

El proceso:
1. Construye la imagen Docker
2. Sube a Fly.io
3. Inicia los contenedores
4. Ejecuta health checks
5. ¡Listo!

**Espera ~2-3 minutos.**

### 3.4 Verificar despliegue

```bash
flyctl status -a taller-docker-backend
flyctl logs -a taller-docker-backend
```

Accede a:
```
https://taller-docker-backend.fly.dev/api/info
```

---

## 🎨 PASO 4: Desplegar Frontend (Nginx)

### 4.1 Crear la app frontend en Fly.io

```bash
flyctl apps create taller-docker-frontend
```

### 4.2 Desplegar el frontend

```bash
flyctl deploy \
  --config fly-frontend.toml \
  --app taller-docker-frontend
```

### 4.3 Configurar proxy inverso (Nginx)

En `frontend/nginx.conf`, asegúrate de apuntar al backend:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://taller-docker-backend.fly.dev;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.4 Redeploy del frontend

```bash
flyctl deploy \
  --config fly-frontend.toml \
  --app taller-docker-frontend
```

### 4.5 Verificar despliegue

```bash
flyctl status -a taller-docker-frontend
flyctl logs -a taller-docker-frontend
```

Accede a:
```
https://taller-docker-frontend.fly.dev
```

---

## 🌐 PASO 5: Conectar Frontend ↔ Backend

### 5.1 Obtener URLs públicas

```bash
flyctl info -a taller-docker-backend
flyctl info -a taller-docker-frontend
```

Verás algo como:
- Backend: `https://taller-docker-backend.fly.dev`
- Frontend: `https://taller-docker-frontend.fly.dev`

### 5.2 Actualizar variables de entorno

En el frontend, actualiza `nginx.conf` con la URL real del backend:

```nginx
location /api/ {
    proxy_pass https://taller-docker-backend.fly.dev;
    # ... resto de configuración
}
```

### 5.3 Redeploy

```bash
flyctl deploy --config fly-frontend.toml --app taller-docker-frontend
```

---

## ✅ PASO 6: Verificación Final

### 6.1 Verificar todos los servicios

```bash
# Ver status de backend
flyctl status -a taller-docker-backend

# Ver status de frontend
flyctl status -a taller-docker-frontend

# Ver logs de backend
flyctl logs -a taller-docker-backend -n 50

# Ver logs de frontend
flyctl logs -a taller-docker-frontend -n 50
```

### 6.2 Pruebas de conectividad

```bash
# Test backend
curl https://taller-docker-backend.fly.dev/health

# Test frontend
curl https://taller-docker-frontend.fly.dev

# Test API desde el navegador
# Abre: https://taller-docker-frontend.fly.dev/api/info
```

---

## 🔐 SEGURIDAD

### Variables sensibles (NO versionarlas)

```bash
# Nunca hagas git add en .env
git add .env        # ❌ MAL
git add .env.*      # ❌ MAL

# Usar secrets de Fly.io
flyctl secrets set DATABASE_URL=...
flyctl secrets list -a taller-docker-backend
```

### .gitignore debe contener:

```
.env
.env.local
.env.*.local
```

---

## 🔄 ACTUALIZACIONES Y REDEPLOY

Cuando hagas cambios:

```bash
# Backend
git add .
git commit -m "Update: cambios en Flask"
flyctl deploy --config fly-backend.toml --app taller-docker-backend

# Frontend
git add .
git commit -m "Update: cambios en HTML/Nginx"
flyctl deploy --config fly-frontend.toml --app taller-docker-frontend
```

---

## 🐛 TROUBLESHOOTING

### Error: "Connection refused"
```bash
# Verifica si la app está corriendo
flyctl status -a taller-docker-backend
flyctl status -a taller-docker-frontend

# Ver logs detallados
flyctl logs -a taller-docker-backend
```

### Error: "DATABASE_URL not found"
```bash
# Asegúrate de haber configurado secrets
flyctl secrets list -a taller-docker-backend

# Si falta, agregarlo
flyctl secrets set DATABASE_URL=postgres://... --app taller-docker-backend
```

### Error: "Health check failing"
```bash
# Ver health check logs
flyctl logs -a taller-docker-backend

# Verificar endpoint /health
curl https://taller-docker-backend.fly.dev/health
```

### Error: "Build failed"
```bash
# Ver logs de build completo
flyctl logs -a taller-docker-backend --verbose

# Asegúrate de que Dockerfile existe:
ls -la frontend/Dockerfile
ls -la backend/Dockerfile
```

---

## 📊 MONITOREO

### Ver métricas en tiempo real

```bash
# CPU, Memoria, etc.
flyctl status -a taller-docker-backend
flyctl metrics -a taller-docker-backend
```

### Dashboard web

Ve a https://fly.io/dashboard para:
- Ver todas tus apps
- Monitoreo en tiempo real
- Escalar máquinas
- Ver facturación

---

## 💰 COSTOS

**Tier gratuito de Fly.io incluye:**
- ✅ 3 máquinas compartidas (shared-cpu-1x)
- ✅ 3 GB almacenamiento
- ✅ 160 GB datos transferidos/mes
- ✅ PostgreSQL pequeño gratuito

**Tu setup:**
- 2 apps (backend + frontend) = dentro del gratuito
- PostgreSQL integrado = dentro del gratuito
- **Total mensual: $0** (si no excedes límites)

---

## 🎯 PRÓXIMOS PASOS

1. ✅ Instalar Fly CLI
2. ✅ Crear PostgreSQL
3. ✅ Desplegar Backend
4. ✅ Desplegar Frontend
5. ✅ Conectar servicios
6. ✅ Verificar en https://tuapp.fly.dev

¿Preguntas? Revisa logs con:
```bash
flyctl logs -a <app-name> --follow
```

---

## 🚀 COMANDOS ÚTILES

```bash
# Ver todas tus apps
flyctl apps list

# Información detallada
flyctl info -a taller-docker-backend

# Ver variables de entorno
flyctl secrets list -a taller-docker-backend

# SSH a la máquina (debug)
flyctl ssh console -a taller-docker-backend

# Redimensionar máquina
flyctl scale vm shared-cpu-2x -a taller-docker-backend

# Destruir app (⚠️ irreversible)
flyctl apps destroy taller-docker-backend

# Ver estado de PostgreSQL
flyctl postgres status -a taller-db
```
