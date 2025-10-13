#!/bin/bash
# Script para iniciar el frontend de LoL Wrapped

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 LoL Wrapped - Frontend Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Paso 1: Verificar .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    echo "Ejecutando setup..."
    ./setup-env.sh
fi

# Paso 2: Verificar node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    npm install
    echo -e "${GREEN}✅ Dependencias instaladas${NC}\n"
fi

# Paso 3: Mostrar configuración
echo -e "${BLUE}📋 Configuración actual:${NC}"
if [ -f ".env" ]; then
    cat .env | grep PUBLIC_
    echo ""
fi

# Paso 4: Iniciar servidor
echo -e "${GREEN}🚀 Iniciando servidor de desarrollo...${NC}"
echo -e "${BLUE}URL: http://localhost:4321${NC}\n"

npm run dev


