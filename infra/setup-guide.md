# 🚀 Guía de Setup - Fase 1: AppSync + DynamoDB

Esta guía te ayudará a configurar la infraestructura AWS necesaria para el League of Legends Wrapped.

## 📋 Prerequisitos

- Cuenta de AWS
- AWS CLI configurado
- Permisos para crear: DynamoDB, AppSync, IAM roles

## 🗄️ Paso 1: Crear Tabla DynamoDB

### Opción A: Usando la Consola AWS

1. Ve a **DynamoDB** en la consola de AWS
2. Click en **Create table**
3. Configuración:
   ```
   Table name: PlayerWrappeds
   Partition key: PK (String)
   Sort key: SK (String)
   ```
4. En **Table settings**: Usar "On-demand" (no necesitas provisionar capacidad)
5. **Índice Secundario Global (GSI)**:
   - Click en "Create global index"
   - Index name: `GSI1`
   - Partition key: `GSI1PK` (String)
   - Sort key: `GSI1SK` (String)
6. **Time to Live (TTL)**:
   - En la tabla creada, ve a pestaña "Additional settings"
   - Enable TTL
   - TTL attribute: `ttl`

### Opción B: Usando AWS CLI

```bash
aws dynamodb create-table \
  --table-name PlayerWrappeds \
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
  --region us-east-1

# Habilitar TTL
aws dynamodb update-time-to-live \
  --table-name PlayerWrappeds \
  --time-to-live-specification "Enabled=true, AttributeName=ttl" \
  --region us-east-1
```

## 🔌 Paso 2: Crear API de AppSync

### Usando la Consola AWS

1. Ve a **AWS AppSync** en la consola
2. Click en **Create API**
3. Selecciona **Build from scratch**
4. API name: `LoLWrappedAPI`
5. Click **Create**

### Configurar el Schema

1. En tu API, ve a **Schema** en el menú lateral
2. Copia y pega el contenido de `infra/schema.graphql`
3. Click **Save Schema**

### Configurar Data Source (DynamoDB)

1. Ve a **Data sources** en el menú lateral
2. Click **Create data source**
3. Configuración:
   ```
   Data source name: PlayerWrappedsDynamoDB
   Data source type: Amazon DynamoDB table
   Region: us-east-1
   Table name: PlayerWrappeds
   ```
4. **IAM Role**:
   - Selecciona "Create new role"
   - AWS creará automáticamente el rol con permisos necesarios
5. Click **Create**

### Configurar Resolvers

Para cada resolver, haz lo siguiente:

#### 1. Query.getWrapped

1. Ve a **Schema** → Encuentra `getWrapped` en tipo `Query`
2. Click en **Attach** al lado de `getWrapped`
3. Selecciona data source: `PlayerWrappedsDynamoDB`
4. En **Configure the request mapping template**:
   - Copia el contenido de `infra/resolvers/Query.getWrapped.req.vtl`
5. En **Configure the response mapping template**:
   - Copia el contenido de `infra/resolvers/Query.getWrapped.res.vtl`
6. Click **Save Resolver**

#### 2. Mutation.requestWrapped

1. Ve a **Schema** → Encuentra `requestWrapped` en tipo `Mutation`
2. Click en **Attach**
3. Selecciona data source: `PlayerWrappedsDynamoDB`
4. Request template: `infra/resolvers/Mutation.requestWrapped.req.vtl`
5. Response template: `infra/resolvers/Mutation.requestWrapped.res.vtl`
6. **Save**

#### 3. Mutation.updateWrappedStatus

1. Encuentra `updateWrappedStatus` en tipo `Mutation`
2. Click en **Attach**
3. Selecciona data source: `PlayerWrappedsDynamoDB`
4. Request template: `infra/resolvers/Mutation.updateWrappedStatus.req.vtl`
5. Response template: `infra/resolvers/Mutation.updateWrappedStatus.res.vtl`
6. **Save**

## 🔑 Paso 3: Configurar Autenticación

Para esta fase usaremos API Key (simple):

1. En tu API de AppSync, ve a **Settings**
2. En **Authorization modes**:
   - Default: **API Key**
   - Click **Create default authorization mode**
3. Se generará una API Key automáticamente
4. **¡Guarda esta API Key!** La necesitarás para el frontend

## 📝 Paso 4: Obtener información de configuración

Necesitarás estos valores para el frontend:

1. **GraphQL endpoint**:
   - Ve a **Settings** → Copia el **API URL**
   - Ejemplo: `https://xxxxx.appsync-api.us-east-1.amazonaws.com/graphql`

2. **API Key**:
   - Ve a **Settings** → **API Keys** → Copia la key
   - Ejemplo: `da2-xxxxxxxxxxxxx`

3. **Region**: `us-east-1` (o la región que elegiste)

## 🧪 Paso 5: Probar la API

1. En AppSync, ve a **Queries** en el menú lateral
2. Prueba esta query:

```graphql
# Solicitar generación de wrapped
mutation RequestWrapped {
  requestWrapped(
    gameName: "NamiNami"
    tagLine: "LAN"
    region: "la1"
    year: 2025
  ) {
    playerId
    status
    gameName
    tagLine
    requestedAt
  }
}
```

3. Luego consulta el estado:

```graphql
# Obtener wrapped
query GetWrapped {
  getWrapped(
    playerId: "NamiNami#LAN"
    year: 2025
  ) {
    playerId
    status
    gameName
    tagLine
    requestedAt
  }
}
```

Deberías ver `status: "PROCESSING"`

## 📊 Paso 6: Verificar en DynamoDB

1. Ve a **DynamoDB** → **Tables** → **PlayerWrappeds**
2. Click en **Explore table items**
3. Deberías ver tu item con:
   - `PK`: `PLAYER#NamiNami#LAN`
   - `SK`: `WRAPPED#2025`
   - `status`: `PROCESSING`

## ✅ ¡Listo!

Ahora tienes:
- ✅ Tabla DynamoDB configurada
- ✅ API GraphQL funcionando
- ✅ Queries y Mutations operativas

## 🔜 Próximos pasos

Configura el frontend con los valores obtenidos:

```bash
# En landing/.env
PUBLIC_APPSYNC_ENDPOINT=https://xxxxx.appsync-api.us-east-1.amazonaws.com/graphql
PUBLIC_APPSYNC_API_KEY=da2-xxxxxxxxxxxxx
PUBLIC_APPSYNC_REGION=us-east-1
```

## 🐛 Troubleshooting

### Error: "Unauthorized"
- Verifica que la API Key esté activa
- Verifica que la API Key esté en el header de la request

### Error: "Unable to access DynamoDB"
- Verifica que el IAM Role tenga permisos correctos
- Ve a IAM → Roles → Busca el rol de AppSync
- Debe tener permisos: `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:UpdateItem`

### No aparecen items en DynamoDB
- Verifica que los resolvers estén correctamente configurados
- Revisa los CloudWatch Logs de AppSync para ver errores


