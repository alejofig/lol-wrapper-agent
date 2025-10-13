#!/bin/bash
# Script para probar que DynamoDB funciona correctamente
# Crea un item de prueba y lo consulta

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
PROJECT_NAME="lol-wrapped"
ENVIRONMENT="dev"
REGION="us-east-1"
TABLE_NAME="${PROJECT_NAME}-${ENVIRONMENT}-PlayerWrappeds"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🧪 Testing DynamoDB Connection${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Verificar que la tabla existe
echo -e "${YELLOW}📊 Verificando tabla DynamoDB...${NC}"
if ! aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" &> /dev/null; then
    echo -e "${RED}❌ Tabla $TABLE_NAME no existe${NC}"
    echo "Ejecuta primero: ./infra/deploy.sh"
    exit 1
fi

echo -e "${GREEN}✅ Tabla encontrada: ${TABLE_NAME}${NC}\n"

# Datos de prueba
TEST_PLAYER="TestPlayer#TEST"
TEST_YEAR="2025"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TTL=$(($(date +%s) + 86400))  # 24 horas desde ahora

echo -e "${BLUE}📝 Paso 1: Escribiendo item de prueba...${NC}"
echo "  - Player: ${TEST_PLAYER}"
echo "  - Year: ${TEST_YEAR}"
echo "  - Status: PROCESSING"
echo ""

# Crear item
aws dynamodb put-item \
    --table-name "$TABLE_NAME" \
    --item "{
        \"PK\": {\"S\": \"PLAYER#${TEST_PLAYER}\"},
        \"SK\": {\"S\": \"WRAPPED#${TEST_YEAR}\"},
        \"status\": {\"S\": \"PROCESSING\"},
        \"gameName\": {\"S\": \"TestPlayer\"},
        \"tagLine\": {\"S\": \"TEST\"},
        \"region\": {\"S\": \"na1\"},
        \"requestedAt\": {\"S\": \"${TIMESTAMP}\"},
        \"ttl\": {\"N\": \"${TTL}\"},
        \"GSI1PK\": {\"S\": \"STATUS#PROCESSING\"},
        \"GSI1SK\": {\"S\": \"${TIMESTAMP}\"}
    }" \
    --region "$REGION"

echo -e "${GREEN}✅ Item creado exitosamente${NC}\n"

# Leer item
echo -e "${BLUE}📖 Paso 2: Leyendo item...${NC}"

ITEM=$(aws dynamodb get-item \
    --table-name "$TABLE_NAME" \
    --key "{
        \"PK\": {\"S\": \"PLAYER#${TEST_PLAYER}\"},
        \"SK\": {\"S\": \"WRAPPED#${TEST_YEAR}\"}
    }" \
    --region "$REGION" \
    --output json)

if [ -z "$ITEM" ] || [ "$ITEM" == "null" ]; then
    echo -e "${RED}❌ No se pudo leer el item${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Item leído exitosamente${NC}"
echo ""
echo "Item completo:"
echo "$ITEM" | jq '.Item'
echo ""

# Actualizar item a COMPLETED
echo -e "${BLUE}🔄 Paso 3: Actualizando item a COMPLETED...${NC}"

COMPLETED_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

aws dynamodb update-item \
    --table-name "$TABLE_NAME" \
    --key "{
        \"PK\": {\"S\": \"PLAYER#${TEST_PLAYER}\"},
        \"SK\": {\"S\": \"WRAPPED#${TEST_YEAR}\"}
    }" \
    --update-expression "SET #status = :status, completedAt = :completedAt, wrappedData = :data" \
    --expression-attribute-names "{\"#status\": \"status\"}" \
    --expression-attribute-values "{
        \":status\": {\"S\": \"COMPLETED\"},
        \":completedAt\": {\"S\": \"${COMPLETED_TIMESTAMP}\"},
        \":data\": {\"S\": \"{\\\"test\\\": \\\"data\\\", \\\"games\\\": 10}\"}
    }" \
    --region "$REGION"

echo -e "${GREEN}✅ Item actualizado${NC}\n"

# Verificar actualización
echo -e "${BLUE}📖 Paso 4: Verificando actualización...${NC}"

UPDATED_ITEM=$(aws dynamodb get-item \
    --table-name "$TABLE_NAME" \
    --key "{
        \"PK\": {\"S\": \"PLAYER#${TEST_PLAYER}\"},
        \"SK\": {\"S\": \"WRAPPED#${TEST_YEAR}\"}
    }" \
    --region "$REGION" \
    --output json)

STATUS=$(echo "$UPDATED_ITEM" | jq -r '.Item.status.S')

if [ "$STATUS" == "COMPLETED" ]; then
    echo -e "${GREEN}✅ Estado actualizado correctamente a: ${STATUS}${NC}"
else
    echo -e "${RED}❌ Error: Estado es ${STATUS}, debería ser COMPLETED${NC}"
    exit 1
fi

echo ""
echo "Item actualizado:"
echo "$UPDATED_ITEM" | jq '.Item'
echo ""

# Query por GSI (buscar todos los PROCESSING)
echo -e "${BLUE}🔍 Paso 5: Consultando por GSI (items en PROCESSING)...${NC}"

# Primero crear otro item PROCESSING para la prueba
aws dynamodb put-item \
    --table-name "$TABLE_NAME" \
    --item "{
        \"PK\": {\"S\": \"PLAYER#AnotherPlayer#TEST\"},
        \"SK\": {\"S\": \"WRAPPED#${TEST_YEAR}\"},
        \"status\": {\"S\": \"PROCESSING\"},
        \"gameName\": {\"S\": \"AnotherPlayer\"},
        \"tagLine\": {\"S\": \"TEST\"},
        \"region\": {\"S\": \"la1\"},
        \"requestedAt\": {\"S\": \"${TIMESTAMP}\"},
        \"ttl\": {\"N\": \"${TTL}\"},
        \"GSI1PK\": {\"S\": \"STATUS#PROCESSING\"},
        \"GSI1SK\": {\"S\": \"${TIMESTAMP}\"}
    }" \
    --region "$REGION" \
    --return-consumed-capacity TOTAL

GSI_RESULTS=$(aws dynamodb query \
    --table-name "$TABLE_NAME" \
    --index-name "GSI1" \
    --key-condition-expression "GSI1PK = :status" \
    --expression-attribute-values "{\":status\": {\"S\": \"STATUS#PROCESSING\"}}" \
    --region "$REGION" \
    --output json)

PROCESSING_COUNT=$(echo "$GSI_RESULTS" | jq '.Count')

echo -e "${GREEN}✅ Query ejecutado exitosamente${NC}"
echo "  - Items encontrados: ${PROCESSING_COUNT}"
echo ""

# Limpiar - Eliminar items de prueba
echo -e "${YELLOW}🧹 Paso 6: Limpiando items de prueba...${NC}"

aws dynamodb delete-item \
    --table-name "$TABLE_NAME" \
    --key "{
        \"PK\": {\"S\": \"PLAYER#${TEST_PLAYER}\"},
        \"SK\": {\"S\": \"WRAPPED#${TEST_YEAR}\"}
    }" \
    --region "$REGION"

aws dynamodb delete-item \
    --table-name "$TABLE_NAME" \
    --key "{
        \"PK\": {\"S\": \"PLAYER#AnotherPlayer#TEST\"},
        \"SK\": {\"S\": \"WRAPPED#${TEST_YEAR}\"}
    }" \
    --region "$REGION"

echo -e "${GREEN}✅ Items de prueba eliminados${NC}\n"

# Resumen
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Todas las pruebas pasaron!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}✨ DynamoDB está funcionando correctamente:${NC}"
echo "  ✅ Crear items (PutItem)"
echo "  ✅ Leer items (GetItem)"
echo "  ✅ Actualizar items (UpdateItem)"
echo "  ✅ Consultar por índice (Query GSI1)"
echo "  ✅ Eliminar items (DeleteItem)"
echo ""

echo -e "${YELLOW}📋 Próximos pasos:${NC}"
echo "1. Configura AppSync (schema + resolvers)"
echo "2. Configura frontend (.env con API endpoint)"
echo "3. Prueba el flujo completo desde el frontend"
echo ""

echo -e "${BLUE}🔗 Ver items en DynamoDB Console:${NC}"
echo "https://${REGION}.console.aws.amazon.com/dynamodbv2/home?region=${REGION}#table?name=${TABLE_NAME}"
echo ""


