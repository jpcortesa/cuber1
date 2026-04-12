#!/bin/bash
# ============================================================
# Script de Despliegue Automático - Fly.io
# Uso: ./deploy-flyio.sh
# ============================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Script de Despliegue Fly.io${NC}"
echo "======================================"

# 1. Verificar que Fly CLI está instalado
echo -e "${YELLOW}[1/5] Verificando Fly CLI...${NC}"
if ! command -v flyctl &> /dev/null; then
    echo -e "${RED}❌ Fly CLI no está instalado${NC}"
    echo "Instala desde: https://fly.io/docs/getting-started/installing-flyctl/"
    exit 1
fi
echo -e "${GREEN}✅ Fly CLI encontrado${NC}"

# 2. Verificar autenticación
echo -e "${YELLOW}[2/5] Verificando autenticación...${NC}"
if ! flyctl auth whoami &> /dev/null; then
    echo -e "${RED}❌ No autenticado en Fly.io${NC}"
    echo "Ejecuta: flyctl auth login"
    exit 1
fi
USER=$(flyctl auth whoami)
echo -e "${GREEN}✅ Autenticado como: $USER${NC}"

# 3. Crear PostgreSQL (si no existe)
echo -e "${YELLOW}[3/5] Verificando PostgreSQL...${NC}"
if flyctl apps list | grep -q "taller-db"; then
    echo -e "${GREEN}✅ Base de datos ya existe${NC}"
else
    echo "Creando PostgreSQL..."
    flyctl postgres create \
        --name taller-db \
        --region scl \
        --vm-size shared-cpu-1x \
        --initial-cluster-size 1 \
        --skip-launch
    echo -e "${GREEN}✅ PostgreSQL creado${NC}"
fi

# 4. Desplegar Backend
echo -e "${YELLOW}[4/5] Desplegando Backend...${NC}"
if flyctl apps list | grep -q "taller-docker-backend"; then
    echo "Actualizando backend existente..."
else
    echo "Creando app backend..."
    flyctl launch \
        --path . \
        --name taller-docker-backend \
        --no-deploy \
        --region scl
fi

echo "Configurando variables de entorno..."
read -sp "PostgreSQL URL (o Enter para auto): " DB_URL
if [ -z "$DB_URL" ]; then
    DB_URL="postgres://talleruser:tallerpass@taller-db.internal/tallerdb"
fi

flyctl secrets set \
    DATABASE_URL="$DB_URL" \
    FLASK_ENV=production \
    --app taller-docker-backend

echo "Desplegando backend..."
flyctl deploy \
    --config fly-backend.toml \
    --app taller-docker-backend \
    --build-arg DB_USER=talleruser \
    --build-arg DB_NAME=tallerdb

echo -e "${GREEN}✅ Backend desplegado${NC}"

# 5. Desplegar Frontend
echo -e "${YELLOW}[5/5] Desplegando Frontend...${NC}"
if flyctl apps list | grep -q "taller-docker-frontend"; then
    echo "Actualizando frontend existente..."
else
    echo "Creando app frontend..."
    flyctl launch \
        --path . \
        --name taller-docker-frontend \
        --no-deploy \
        --region scl
fi

echo "Desplegando frontend..."
flyctl deploy \
    --config fly-frontend.toml \
    --app taller-docker-frontend

echo -e "${GREEN}✅ Frontend desplegado${NC}"

# Resumen
echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ ¡DESPLIEGUE COMPLETADO!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "URLs de acceso:"
echo -e "${YELLOW}Backend:${NC}  https://taller-docker-backend.fly.dev"
echo -e "${YELLOW}Frontend:${NC} https://taller-docker-frontend.fly.dev"
echo ""
echo "Comandos útiles:"
echo "  Ver estado:     flyctl status -a taller-docker-backend"
echo "  Ver logs:       flyctl logs -a taller-docker-backend --follow"
echo "  Redeploy:       flyctl deploy --config fly-backend.toml --app taller-docker-backend"
echo ""
