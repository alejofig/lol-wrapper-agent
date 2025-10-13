#!/bin/bash
# Script para configurar los resolvers de AppSync via CLI

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
API_ID="zdp4tx5muvbe7dt7oipu4r76iq"
REGION="us-east-1"
DATA_SOURCE_NAME="PlayerWrappedsDynamoDB"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔧 Configurando Resolvers de AppSync${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Función para crear resolver
create_resolver() {
    local TYPE_NAME=$1
    local FIELD_NAME=$2
    local REQ_TEMPLATE=$3
    local RES_TEMPLATE=$4
    
    echo -e "${YELLOW}📝 Configurando resolver: ${TYPE_NAME}.${FIELD_NAME}${NC}"
    
    # Eliminar resolver si ya existe
    aws appsync delete-resolver \
        --api-id "$API_ID" \
        --type-name "$TYPE_NAME" \
        --field-name "$FIELD_NAME" \
        --region "$REGION" 2>/dev/null || true
    
    # Crear resolver
    aws appsync create-resolver \
        --api-id "$API_ID" \
        --type-name "$TYPE_NAME" \
        --field-name "$FIELD_NAME" \
        --data-source-name "$DATA_SOURCE_NAME" \
        --request-mapping-template "file://${SCRIPT_DIR}/resolvers/${REQ_TEMPLATE}" \
        --response-mapping-template "file://${SCRIPT_DIR}/resolvers/${RES_TEMPLATE}" \
        --region "$REGION" \
        --output json > /dev/null
    
    echo -e "${GREEN}✅ Resolver ${TYPE_NAME}.${FIELD_NAME} configurado${NC}\n"
}

# Crear los 3 resolvers
echo -e "${BLUE}Creando resolvers...${NC}\n"

create_resolver "Query" "getWrapped" \
    "Query.getWrapped.req.vtl" \
    "Query.getWrapped.res.vtl"

create_resolver "Mutation" "requestWrapped" \
    "Mutation.requestWrapped.req.vtl" \
    "Mutation.requestWrapped.res.vtl"

create_resolver "Mutation" "updateWrappedStatus" \
    "Mutation.updateWrappedStatus.req.vtl" \
    "Mutation.updateWrappedStatus.res.vtl"

# Verificar
echo -e "${BLUE}🔍 Verificando resolvers...${NC}"
RESOLVER_COUNT=$(aws appsync list-resolvers \
    --api-id "$API_ID" \
    --type-name "Query" \
    --region "$REGION" \
    --query 'length(resolvers)' \
    --output text)

echo -e "${GREEN}✅ ${RESOLVER_COUNT} resolver(s) de Query configurados${NC}"

MUTATION_COUNT=$(aws appsync list-resolvers \
    --api-id "$API_ID" \
    --type-name "Mutation" \
    --region "$REGION" \
    --query 'length(resolvers)' \
    --output text)

echo -e "${GREEN}✅ ${MUTATION_COUNT} resolver(s) de Mutation configurados${NC}\n"

# Mostrar resumen
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Resolvers Configurados Exitosamente${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}📋 Resolvers creados:${NC}"
echo "  ✅ Query.getWrapped"
echo "  ✅ Mutation.requestWrapped"
echo "  ✅ Mutation.updateWrappedStatus"
echo ""

echo -e "${YELLOW}🎯 Próximo paso:${NC}"
echo "Actualiza tu navegador y prueba la app en:"
echo "http://localhost:4321/wrapped/NamiNami-LAN"
echo ""


