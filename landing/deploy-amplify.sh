#!/bin/bash
# Script para facilitar el despliegue en AWS Amplify

set -e  # Exit on error

echo "🚀 LoL Wrapped - Despliegue en AWS Amplify"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Debes ejecutar este script desde la carpeta landing/${NC}"
    exit 1
fi

# Verificar que AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está instalado${NC}"
    echo "Instálalo con: brew install awscli (macOS) o pip install awscli"
    exit 1
fi

# Verificar que node/npm están instalados
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm no está instalado${NC}"
    exit 1
fi

echo "✅ Prerequisitos verificados"
echo ""

# Paso 1: Verificar variables de entorno
echo "📋 Paso 1: Verificación de Variables de Entorno"
echo "------------------------------------------------"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    echo ""
    echo "Creando .env desde template..."
    cp env.template .env
    echo -e "${YELLOW}⚠️  Por favor edita el archivo .env con tus credenciales de AppSync${NC}"
    echo ""
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Leer variables de .env
source .env 2>/dev/null || true

if [ -z "$PUBLIC_APPSYNC_ENDPOINT" ]; then
    echo -e "${YELLOW}⚠️  PUBLIC_APPSYNC_ENDPOINT no está configurado${NC}"
    read -p "Ingresa el AppSync Endpoint: " PUBLIC_APPSYNC_ENDPOINT
    echo "PUBLIC_APPSYNC_ENDPOINT=$PUBLIC_APPSYNC_ENDPOINT" >> .env
fi

if [ -z "$PUBLIC_APPSYNC_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  PUBLIC_APPSYNC_API_KEY no está configurado${NC}"
    read -p "Ingresa el AppSync API Key: " PUBLIC_APPSYNC_API_KEY
    echo "PUBLIC_APPSYNC_API_KEY=$PUBLIC_APPSYNC_API_KEY" >> .env
fi

if [ -z "$PUBLIC_APPSYNC_REGION" ]; then
    PUBLIC_APPSYNC_REGION="us-east-1"
    echo "PUBLIC_APPSYNC_REGION=$PUBLIC_APPSYNC_REGION" >> .env
fi

echo -e "${GREEN}✅ Variables de entorno configuradas${NC}"
echo ""

# Paso 2: Instalar dependencias
echo "📦 Paso 2: Instalación de Dependencias"
echo "--------------------------------------"
npm ci
echo -e "${GREEN}✅ Dependencias instaladas${NC}"
echo ""

# Paso 3: Build local (para verificar)
echo "🔨 Paso 3: Build de Prueba"
echo "-------------------------"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build exitoso${NC}"
else
    echo -e "${RED}❌ Build falló - verifica errores arriba${NC}"
    exit 1
fi
echo ""

# Paso 4: Configurar Amplify
echo "⚙️  Paso 4: Configuración de AWS Amplify"
echo "---------------------------------------"

read -p "¿Quieres crear una nueva app en Amplify? (s/n): " CREATE_APP

if [ "$CREATE_APP" = "s" ] || [ "$CREATE_APP" = "S" ]; then
    read -p "Nombre de la app [lol-wrapped-landing]: " APP_NAME
    APP_NAME=${APP_NAME:-lol-wrapped-landing}
    
    read -p "URL del repositorio Git: " REPO_URL
    
    read -p "Región AWS [us-east-1]: " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    
    echo "Creando app en Amplify..."
    
    APP_ID=$(aws amplify create-app \
        --name "$APP_NAME" \
        --repository "$REPO_URL" \
        --region "$AWS_REGION" \
        --query 'app.appId' \
        --output text)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ App creada: $APP_ID${NC}"
        echo "APP_ID=$APP_ID" >> .env
    else
        echo -e "${RED}❌ Error creando app${NC}"
        exit 1
    fi
    
    # Crear rama
    read -p "Nombre de la rama [main]: " BRANCH_NAME
    BRANCH_NAME=${BRANCH_NAME:-main}
    
    aws amplify create-branch \
        --app-id "$APP_ID" \
        --branch-name "$BRANCH_NAME" \
        --region "$AWS_REGION"
    
    # Configurar variables de entorno en Amplify
    echo "Configurando variables de entorno en Amplify..."
    aws amplify update-app \
        --app-id "$APP_ID" \
        --environment-variables \
            PUBLIC_APPSYNC_ENDPOINT="$PUBLIC_APPSYNC_ENDPOINT",\
            PUBLIC_APPSYNC_API_KEY="$PUBLIC_APPSYNC_API_KEY",\
            PUBLIC_APPSYNC_REGION="$PUBLIC_APPSYNC_REGION" \
        --region "$AWS_REGION"
    
    echo -e "${GREEN}✅ Variables de entorno configuradas en Amplify${NC}"
    
    # Iniciar deployment
    echo "Iniciando deployment..."
    JOB_ID=$(aws amplify start-job \
        --app-id "$APP_ID" \
        --branch-name "$BRANCH_NAME" \
        --job-type RELEASE \
        --region "$AWS_REGION" \
        --query 'jobSummary.jobId' \
        --output text)
    
    echo -e "${GREEN}✅ Deployment iniciado: $JOB_ID${NC}"
    echo ""
    echo "🌐 URL de la app:"
    aws amplify get-app --app-id "$APP_ID" --region "$AWS_REGION" --query 'app.defaultDomain' --output text
    echo ""
    echo "Para ver el progreso:"
    echo "  aws amplify get-job --app-id $APP_ID --branch-name $BRANCH_NAME --job-id $JOB_ID --region $AWS_REGION"
    
else
    echo "Usa AWS Amplify Console para configurar manualmente:"
    echo "https://console.aws.amazon.com/amplify"
fi

echo ""
echo "🎉 Proceso completado!"
echo ""
echo "Próximos pasos:"
echo "1. Verifica el deployment en AWS Amplify Console"
echo "2. Configura un dominio personalizado (opcional)"
echo "3. Habilita HTTPS y CDN (incluido automáticamente)"
echo "4. Configura CI/CD para deployments automáticos"
echo ""
echo "Para más información, consulta: ./DEPLOYMENT.md"

