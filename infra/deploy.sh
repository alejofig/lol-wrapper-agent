#!/bin/bash
# Script de deployment para infraestructura de LoL Wrapped
# Usa CloudFormation para crear DynamoDB + AppSync

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_NAME="lol-wrapped"
ENVIRONMENT="dev"
REGION="us-east-1"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-infrastructure"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 LoL Wrapped - Infrastructure Deployment${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Verificar que AWS CLI esté instalado
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está instalado${NC}"
    echo "Instala AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Verificar credenciales de AWS
echo -e "${YELLOW}🔑 Verificando credenciales de AWS...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ No hay credenciales de AWS configuradas${NC}"
    echo "Ejecuta: aws configure"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ Conectado a cuenta AWS: ${AWS_ACCOUNT}${NC}\n"

# Preguntar confirmación
echo -e "${YELLOW}📋 Configuración:${NC}"
echo "  - Stack Name: ${STACK_NAME}"
echo "  - Region: ${REGION}"
echo "  - Project: ${PROJECT_NAME}"
echo "  - Environment: ${ENVIRONMENT}"
echo ""
read -p "¿Continuar con el deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelado${NC}"
    exit 0
fi

# Paso 1: Crear solo DynamoDB primero (más simple)
echo -e "\n${BLUE}📊 Paso 1: Creando tabla DynamoDB...${NC}"

TABLE_NAME="${PROJECT_NAME}-${ENVIRONMENT}-PlayerWrappeds"

# Verificar si la tabla ya existe
if aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" &> /dev/null; then
    echo -e "${YELLOW}⚠️  La tabla $TABLE_NAME ya existe${NC}"
    read -p "¿Quieres eliminarla y recrearla? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Eliminando tabla existente..."
        aws dynamodb delete-table --table-name "$TABLE_NAME" --region "$REGION"
        echo "Esperando a que se elimine..."
        aws dynamodb wait table-not-exists --table-name "$TABLE_NAME" --region "$REGION"
    else
        echo -e "${GREEN}✅ Usando tabla existente${NC}"
        TABLE_ARN=$(aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" --query 'Table.TableArn' --output text)
    fi
fi

# Crear tabla si no existe
if ! aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" &> /dev/null; then
    aws dynamodb create-table \
        --table-name "$TABLE_NAME" \
        --attribute-definitions \
            AttributeName=PK,AttributeType=S \
            AttributeName=SK,AttributeType=S \
            AttributeName=GSI1PK,AttributeType=S \
            AttributeName=GSI1SK,AttributeType=S \
        --key-schema \
            AttributeName=PK,KeyType=HASH \
            AttributeName=SK,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --global-secondary-indexes \
            "[
                {
                    \"IndexName\": \"GSI1\",
                    \"KeySchema\": [
                        {\"AttributeName\":\"GSI1PK\",\"KeyType\":\"HASH\"},
                        {\"AttributeName\":\"GSI1SK\",\"KeyType\":\"RANGE\"}
                    ],
                    \"Projection\": {\"ProjectionType\":\"ALL\"}
                }
            ]" \
        --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
        --tags \
            Key=Project,Value="$PROJECT_NAME" \
            Key=Environment,Value="$ENVIRONMENT" \
        --region "$REGION"

    echo "Esperando a que la tabla esté activa..."
    aws dynamodb wait table-exists --table-name "$TABLE_NAME" --region "$REGION"

    # Habilitar TTL
    echo "Habilitando TTL..."
    aws dynamodb update-time-to-live \
        --table-name "$TABLE_NAME" \
        --time-to-live-specification "Enabled=true,AttributeName=ttl" \
        --region "$REGION"

    # Habilitar Point-in-Time Recovery
    echo "Habilitando Point-in-Time Recovery..."
    aws dynamodb update-continuous-backups \
        --table-name "$TABLE_NAME" \
        --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
        --region "$REGION"

    TABLE_ARN=$(aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" --query 'Table.TableArn' --output text)
fi

echo -e "${GREEN}✅ Tabla DynamoDB creada: ${TABLE_NAME}${NC}"
echo -e "   ARN: ${TABLE_ARN}\n"

# Paso 2: Crear AppSync API
echo -e "${BLUE}🔌 Paso 2: Creando AppSync API...${NC}"

API_NAME="${PROJECT_NAME}-${ENVIRONMENT}-API"

# Crear API
API_ID=$(aws appsync create-graphql-api \
    --name "$API_NAME" \
    --authentication-type API_KEY \
    --region "$REGION" \
    --query 'graphqlApi.apiId' \
    --output text 2>/dev/null || \
    aws appsync list-graphql-apis --region "$REGION" --query "graphqlApis[?name=='$API_NAME'].apiId" --output text)

if [ -z "$API_ID" ]; then
    echo -e "${RED}❌ Error creando AppSync API${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AppSync API creada: ${API_ID}${NC}"

# Obtener endpoint
API_ENDPOINT=$(aws appsync get-graphql-api --api-id "$API_ID" --region "$REGION" --query 'graphqlApi.uris.GRAPHQL' --output text)

# Crear API Key
echo "Creando API Key..."
API_KEY=$(aws appsync create-api-key \
    --api-id "$API_ID" \
    --region "$REGION" \
    --query 'apiKey.id' \
    --output text 2>/dev/null)

if [ -n "$API_KEY" ]; then
    API_KEY_VALUE=$(aws appsync list-api-keys --api-id "$API_ID" --region "$REGION" --query 'apiKeys[0].id' --output text)
fi

echo -e "${GREEN}✅ API Key creada${NC}\n"

# Paso 3: Crear IAM Role para AppSync
echo -e "${BLUE}🔐 Paso 3: Creando IAM Role...${NC}"

ROLE_NAME="${PROJECT_NAME}-${ENVIRONMENT}-AppSyncServiceRole"

# Crear trust policy
cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "appsync.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Crear role (o obtener ARN si ya existe)
ROLE_ARN=$(aws iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document file:///tmp/trust-policy.json \
    --query 'Role.Arn' \
    --output text 2>/dev/null || \
    aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)

# Crear policy inline
cat > /tmp/dynamodb-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "$TABLE_ARN",
        "$TABLE_ARN/index/*"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "DynamoDBAccess" \
    --policy-document file:///tmp/dynamodb-policy.json

echo -e "${GREEN}✅ IAM Role creado: ${ROLE_ARN}${NC}\n"

# Limpiar archivos temporales
rm -f /tmp/trust-policy.json /tmp/dynamodb-policy.json

# Mostrar resumen
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Completado!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}📊 Recursos Creados:${NC}"
echo "  - DynamoDB Table: ${TABLE_NAME}"
echo "  - AppSync API: ${API_ID}"
echo "  - IAM Role: ${ROLE_NAME}"
echo ""

echo -e "${YELLOW}📋 Variables de Entorno (copia a landing/.env):${NC}"
echo ""
echo "PUBLIC_APPSYNC_ENDPOINT=${API_ENDPOINT}"
echo "PUBLIC_APPSYNC_API_KEY=${API_KEY_VALUE}"
echo "PUBLIC_APPSYNC_REGION=${REGION}"
echo ""

echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "1. Configura el schema GraphQL manualmente en AppSync Console"
echo "2. Configura los resolvers manualmente (ver infra/setup-guide.md)"
echo "3. O usa la consola de AWS para completar la configuración"
echo ""

echo -e "${BLUE}🔗 Enlaces Útiles:${NC}"
echo "  - AppSync Console: https://${REGION}.console.aws.amazon.com/appsync/home?region=${REGION}#/${API_ID}/v1/home"
echo "  - DynamoDB Console: https://${REGION}.console.aws.amazon.com/dynamodbv2/home?region=${REGION}#table?name=${TABLE_NAME}"
echo ""

echo -e "${GREEN}✨ ¡Listo para Fase 1!${NC}\n"

