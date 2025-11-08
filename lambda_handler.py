import asyncio
import json
import logging
import os
from datetime import datetime, UTC
import boto3
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WRAPPED_LAMBDA")

# Cliente DynamoDB with region us-east-1
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = os.getenv('DYNAMODB_TABLE_NAME', 'WrappedRequests')
table = dynamodb.Table(table_name)  

# Configuración del modelo
model_settings = {
    "max_tokens": 64000,
    "temperature": 0.7,
    "frequency_penalty": 0,
    "presence_penalty": 0
}

model = BedrockConverseModel(
    model_name="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    settings=AnthropicModelSettings(**model_settings)
)
mcp_url = os.getenv('MCP_SERVER_URL', 'http://localhost:8080/sse/')

# Pydantic schemas para forzar respuesta JSON estructurada
class PlayerInfo(BaseModel):
    game_name: str
    tag_line: str
    puuid: str
    summoner_level: int
    profile_icon_id: int
    mastery_score: int

class ChampionMastery(BaseModel):
    puuid: str
    championId: int
    championLevel: int
    championPoints: int
    lastPlayTime: int
    splash: Optional[str] = None

class BestGame(BaseModel):
    match_id: str
    champion: str
    kda: float
    kills: int
    deaths: int
    assists: int
    win: bool
    damage: Optional[int] = None
    splash: Optional[str] = None

class ChampionStats(BaseModel):
    champion: str
    games: int
    wins: Optional[int] = None
    winrate: Optional[float] = None
    kda: Optional[float] = None
    avg_kills: Optional[float] = None
    avg_deaths: Optional[float] = None
    avg_assists: Optional[float] = None
    splash: Optional[str] = None

class RoleStats(BaseModel):
    role: str
    games: int

class Statistics(BaseModel):
    total_games: int
    wins: int
    losses: int
    winrate: float
    total_kills: int
    total_deaths: int
    total_assists: int
    avg_kda: float
    total_playtime_minutes: int
    best_game: Optional[BestGame] = None
    worst_game: Optional[BestGame] = None
    pentakills: int = 0
    quadrakills: int = 0
    triplekills: int = 0
    first_bloods: int = 0
    avg_kills: float
    avg_deaths: float
    avg_assists: float
    avg_game_duration: float
    top_champions: List[ChampionStats] = []
    top_roles: List[RoleStats] = []
    champion_details: List[ChampionStats] = []
    temporal_insights: Optional[Dict[str, Any]] = None

class ChallengeCategory(BaseModel):
    current: int
    level: str
    max: int
    percentile: float

class Challenge(BaseModel):
    challenge_id: int
    level: str
    percentile: float
    value: float
    tier: Optional[str] = None

class Challenges(BaseModel):
    total_points: int
    total_level: str
    top_challenges: List[Challenge] = []
    category_breakdown: Dict[str, ChallengeCategory] = {}
    percentile_achievements: List[Challenge] = []
    level_counts: Dict[str, int] = {}
    total_active_challenges: int

class WrappedResponse(BaseModel):
    """Schema Pydantic para forzar respuesta JSON estructurada del Wrapped."""
    player: PlayerInfo
    year: int
    ranked: List[Dict[str, Any]] = []
    top_masteries: List[ChampionMastery] = []
    statistics: Statistics
    challenges: Optional[Challenges] = None
    insights: List[str] = []
    matches_analyzed: int
    generated_at: str

async def generate_wrapped(game_name: str, tag_line: str, region: str, max_matches: int = 100, year: int = 2025):
    """Genera el Wrapped usando el agente MCP con respuesta JSON forzada por Pydantic."""
    logger.info(f"Generando Wrapped para {game_name}#{tag_line}")
    logger.info(f"Conectando a MCP Server en: {mcp_url}")
    
    mcp_server = MCPServerSSE(url=mcp_url)
    
    agent = Agent(
        model=model,
        output_type=WrappedResponse,  
        system_prompt="""Eres un experto en análisis de datos de League of Legends.
        
        REGLAS CRÍTICAS:
        
        1. INTERPRETACIÓN DE RESPUESTAS:
           ✅ Si recibes JSON con "puuid", "gameName", "tagLine" → Usuario ENCONTRADO (exitoso)
           ✅ Si recibes JSON con datos de partidas/stats → Respuesta EXITOSA
           ❌ Solo di "no existe" si recibes JSON con "error": "404" o similar
        
        2. REGIONES (tag → región):
           - LAN → region="la1"
           - LAS → region="la2"
           - NA1 → region="na1"
           - BR1 → region="br1"
           - EUW1 → region="euw1"
           - KR1 → region="kr"
        
        3. FLUJO DE TRABAJO WRAPPED CON IMÁGENES:
           Paso 1: Obtener datos básicos
           - USA get_player_wrapped para obtener TODO el Wrapped
           
           Paso 2: Enriquecer con splash art (OPTIMIZADO)
           - EXTRAE los champion IDs del resultado (busca "championId" en el JSON)
           - LLAMA get_champion_splash_urls con los IDs separados por comas
           - AÑADE la URL de splash a cada campeón en el JSON
           
           Ejemplo:
           Si el Wrapped tiene: {"top_champions": [{"championId": 103}, {"championId": 222}]}
           Entonces llama: get_champion_splash_urls("103,222")
           Recibirás: [{"championId": 103, "name": "Ahri", "splash": "url..."}]
           Y añades solo el campo "splash" al JSON final
        
        4. SALIDA:
           - Devuelve SOLO el objeto JSON estructurado (será validado por Pydantic)
           - Cada campeón debe tener su campo "splash" con la URL
           - NO añadas texto explicativo, SOLO el JSON""",
        mcp_servers=[mcp_server]
    )
    
    user_query = f"""Genera el Wrapped {year} COMPLETO CON SPLASH ART del jugador {game_name}#{tag_line}.
    
    Instrucciones (SIGUE TODOS LOS PASOS):
    
    PASO 1 - Obtener Wrapped:
    Llama get_player_wrapped con estos parámetros:
       - game_name: "{game_name}"
       - tag_line: "{tag_line}"
       - region: "{region}"
       - max_matches: {max_matches}
       - year: {year}
    
    PASO 2 - Enriquecer con splash art (OPTIMIZADO):
    Del JSON resultante, extrae TODOS los championId que encuentres.
    Luego llama get_champion_splash_urls pasando los IDs separados por comas.
    Ejemplo: si encuentras championId 103, 222, 157 → llama get_champion_splash_urls("103,222,157")
    
    Esto te devolverá: [{{"championId": 103, "name": "Ahri", "splash": "url..."}}]
    
    PASO 3 - Combinar datos:
    Toma el JSON del Wrapped y añade SOLO el campo "splash" a cada campeón según su championId.
    
    SALIDA FINAL:
    Devuelve el JSON completo enriquecido con las URLs de splash art.
    NO interpretes, NO resumas, solo devuelve el JSON enriquecido.
    """
    
    try:
        async with agent.run_mcp_servers():
            logger.info("✅ Conectado al servidor MCP")
            logger.info("Ejecutando agente...")
            result = await agent.run(user_query)
            
            # Con output_type=WrappedResponse, el resultado es un AgentRunResult
            # El objeto Pydantic validado está en result.output (no result.data)
            wrapped_data: WrappedResponse = result.output
            logger.info(f"✅ Wrapped validado por Pydantic: {wrapped_data.matches_analyzed} partidas analizadas")
            
            # Convertir a dict para serializar a JSON
            return wrapped_data.model_dump()
    except Exception as e:
        logger.error(f"Error detallado: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


def lambda_handler(event, context):
    """
    Handler de Lambda que procesa eventos de DynamoDB Stream.
    
    Se activa cuando se CREA un nuevo registro en la tabla.
    """
    logger.info(f"Evento recibido: {json.dumps(event)}")
    
    try:
        # Procesar cada registro del stream
        for record in event['Records']:
            # Solo procesar INSERT (nuevas solicitudes)
            if record['eventName'] != 'INSERT':
                logger.info(f"Evento ignorado: {record['eventName']}")
                continue
            
            # Extraer datos del nuevo item
            new_image = record['dynamodb']['NewImage']
            
            # Extraer campos clave
            pk = new_image['PK']['S']  # PLAYER#{gameName}#{tagLine}
            sk = new_image['SK']['S']  # WRAPPED#{year}
            
            # Extraer gameName, tagLine, region
            # Si no existen en el item, parsearlos del PK
            if 'gameName' in new_image and 'tagLine' in new_image:
                game_name = new_image['gameName']['S']
                tag_line = new_image['tagLine']['S']
            else:
                # Parsear del PK: PLAYER#{gameName}#{tagLine}
                parts = pk.split('#')
                game_name = parts[1] if len(parts) > 1 else 'Unknown'
                tag_line = parts[2] if len(parts) > 2 else 'Unknown'
                logger.warning(f"gameName/tagLine no encontrados, parseados del PK: {game_name}#{tag_line}")
            
            # Region (por defecto la1 si no existe)
            region = new_image.get('region', {}).get('S', 'la1')
            
            # Extraer año del SK
            year = int(sk.split('#')[1])
            
            logger.info(f"Procesando solicitud: {pk} - {game_name}#{tag_line} - Año: {year}")
            
            # Actualizar estado a "processing"
            # Agregar campos faltantes si no existen (gameName, tagLine, region, requestedAt)
            now_iso = datetime.now(UTC).isoformat()
            table.update_item(
                Key={'PK': pk, 'SK': sk},
                UpdateExpression='''
                    SET #status = :status, 
                        processingStartTime = :time, 
                        GSI1PK = :gsi1pk,
                        gameName = if_not_exists(gameName, :gameName),
                        tagLine = if_not_exists(tagLine, :tagLine),
                        #region = if_not_exists(#region, :region),
                        requestedAt = if_not_exists(requestedAt, :time)
                ''',
                ExpressionAttributeNames={
                    '#status': 'status',
                    '#region': 'region'
                },
                ExpressionAttributeValues={
                    ':status': 'PROCESSING',
                    ':time': now_iso,
                    ':gsi1pk': 'STATUS#PROCESSING',
                    ':gameName': game_name,
                    ':tagLine': tag_line,
                    ':region': region
                }
            )
            
            try:
                # Generar Wrapped (asíncrono)
                wrapped_data = asyncio.run(
                    generate_wrapped(
                        game_name=game_name,
                        tag_line=tag_line,
                        region=region,
                        max_matches=200, 
                        year=2025
                    )
                )
                # Actualizar DynamoDB con resultado exitoso
                table.update_item(
                    Key={'PK': pk, 'SK': sk},
                    UpdateExpression='''
                        SET #status = :status, 
                            wrappedData = :data,
                            completedAt = :time,
                            GSI1PK = :gsi1pk
                    ''',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':status': 'COMPLETED',
                        ':data': json.dumps(wrapped_data),
                        ':time': datetime.now(UTC).isoformat(),
                        ':gsi1pk': 'STATUS#COMPLETED'
                    }
                )
                
                logger.info(f"✅ Wrapped generado exitosamente para {pk}")

                # Disparar el job de vectorización de forma asíncrona
                try:
                    lambda_client = boto3.client("lambda")
                    player_identifier = pk.replace("PLAYER#", "").replace("#", "-")
                    payload = {"player_identifier": player_identifier}
                    
                    lambda_client.invoke(
                        FunctionName=os.getenv("VECTORIZER_LAMBDA_NAME", "lol-wrapped-vectorizer"),
                        InvocationType="Event",  # Invocación asíncrona
                        Payload=json.dumps(payload)
                    )
                    logger.info(f"🚀 Job de vectorización disparado para {player_identifier}")
                except Exception as e:
                    logger.error(f"Error al disparar el job de vectorización: {str(e)}")

            except Exception as e:
                logger.error(f"❌ Error generando Wrapped: {str(e)}")
                
                # Actualizar DynamoDB con error
                table.update_item(
                    Key={'PK': pk, 'SK': sk},
                    UpdateExpression='''
                        SET #status = :status, 
                            #error = :error,
                            completedAt = :time,
                            GSI1PK = :gsi1pk
                    ''',
                    ExpressionAttributeNames={
                        '#status': 'status',
                        '#error': 'error'
                    },
                    ExpressionAttributeValues={
                        ':status': 'FAILED',
                        ':error': str(e),
                        ':time': datetime.now(UTC).isoformat(),
                        ':gsi1pk': 'STATUS#FAILED'
                    }
                )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Wrapped processing completed')
        }
        
    except Exception as e:
        logger.error(f"Error en lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }


# Para pruebas locales
if __name__ == "__main__":
    # Simular un evento de DynamoDB Stream
    test_event = {
        "Records": [
            {
                "eventName": "INSERT",
                "dynamodb": {
                    "NewImage": {
                        "PK": {"S": "PLAYER#Elxs#LAN"},
                        "SK": {"S": "WRAPPED#2025"},
                        "gameName": {"S": "Elxs"},
                        "tagLine": {"S": "LAN"},
                        "region": {"S": "la1"},
                        "status": {"S": "PROCESSING"},
                        "GSI1PK": {"S": "STATUS#PROCESSING"}
                    }
                }
            }
        ]
    }
    
    lambda_handler(test_event, None)

