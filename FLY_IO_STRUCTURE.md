# 📦 ESTRUCTURA PARA FLY.IO

```
tu-repo/
│
├── 📄 README.md
├── 📄 .gitignore
├── 📄 .env.example
│
├── 🔧 fly-backend.toml        ← Config backend
├── 🔧 fly-frontend.toml       ← Config frontend
├── 📝 deploy-flyio.sh         ← Script de despliegue
│
├── 📁 backend/
│   ├── 📄 Dockerfile          ← Imagen Flask
│   ├── 📄 requirements.txt     ← Dependencias Python
│   ├── 📄 app.py              ← Código Flask
│   ├── 📄 .dockerignore
│   └── 📄 wsgi.py (opcional)
│
└── 📁 frontend/
    ├── 📄 Dockerfile          ← Imagen Nginx
    ├── 📄 nginx.conf          ← Config proxy
    ├── 📄 .dockerignore
    └── 📁 html/
        └── 📄 index.html
```

## ✅ CHECKLIST ANTES DE DESPLEGAR

- [ ] Fly CLI instalado (`flyctl version`)
- [ ] Autenticado (`flyctl auth login`)
- [ ] Dockerfile en `backend/Dockerfile`
- [ ] Dockerfile en `frontend/Dockerfile`
- [ ] `fly-backend.toml` en raíz
- [ ] `fly-frontend.toml` en raíz
- [ ] `nginx.conf` en `frontend/`
- [ ] `app.py` en `backend/` (con endpoints `/health` y `/api/info`)
- [ ] `requirements.txt` en `backend/`
- [ ] `.env.example` con credenciales template
- [ ] `.gitignore` contiene `.env`
- [ ] GitHub repo creado
- [ ] `git add . && git commit && git push`

## 🚀 DESPLIEGUE RÁPIDO (3 PASOS)

```bash
# 1. Hacer ejecutable el script
chmod +x deploy-flyio.sh

# 2. Ejecutar despliegue automático
./deploy-flyio.sh

# 3. Esperar 5-10 minutos y acceder
open https://taller-docker-frontend.fly.dev
```

## 🔗 COMUNICACIÓN ENTRE SERVICIOS EN FLY.IO

```
┌─────────────────────────────────────────────────┐
│ Frontend (Nginx)                                │
│ https://taller-docker-frontend.fly.dev          │
│                                                 │
│  location /api/ {                              │
│      proxy_pass http://backend.internal  ◄──┐  │
│  }                                           │  │
└─────────────────────────────────────────────┼──┘
                                               │
┌──────────────────────────────────────────────┼──┐
│ Backend (Flask)                              │  │
│ https://taller-docker-backend.fly.dev ◄─────┘  │
│                                                 │
│  @app.route('/api/info')                       │
│  DB_HOST = os.getenv('DATABASE_URL')           │
│                  ↓                              │
└──────────────────────────────────────────────┼──┘
                                               │
┌──────────────────────────────────────────────┼──┐
│ PostgreSQL (Fly.io Database)                │  │
│ postgres://talleruser@taller-db.internal ◄─┘  │
└─────────────────────────────────────────────────┘
```

## 🔐 VARIABLES DE ENTORNO EN FLY.IO

**Backend:**
```bash
flyctl secrets set \
  DATABASE_URL=postgres://... \
  FLASK_ENV=production \
  --app taller-docker-backend
```

**Frontend:**
```bash
# Sin secretos requeridos (todo es público)
flyctl scale --app taller-docker-frontend
```

## 📊 MONITOREO

```bash
# Status en tiempo real
flyctl status -a taller-docker-backend
flyctl status -a taller-docker-frontend

# Logs en vivo
flyctl logs -a taller-docker-backend --follow

# Métricas
flyctl metrics -a taller-docker-backend
```

## 💰 COSTOS ESPERADOS

| Concepto | Gratuito | Exceso |
|----------|----------|--------|
| Apps | 3 | $0.0019/hr cada |
| PostgreSQL | 1 pequeño | $0.07/GB-día |
| Data transfer | 160 GB/mes | $0.02/GB |
| **Total** | **$0** | *Si no excedes* |

## 🎓 DIFERENCIAS CON DOCKER-COMPOSE LOCAL

| Aspecto | Local (docker-compose) | Fly.io |
|--------|--------|--------|
| **DB Host** | `db` | `taller-db.internal` |
| **Backend URL** | `http://backend:5000` | `https://backend.fly.dev` |
| **Frontend URL** | `http://localhost:8080` | `https://frontend.fly.dev` |
| **Variables** | `.env` file | `flyctl secrets` |
| **Logs** | `docker-compose logs` | `flyctl logs` |
| **Deploy** | `docker-compose up` | `flyctl deploy` |
