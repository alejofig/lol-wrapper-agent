import asyncio
import logging
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
from dotenv import load_dotenv
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.models.anthropic import AnthropicModelSettings
import os
model_settings = {
    "max_tokens": 64000,
    "temperature": 0.7,
    "frequency_penalty": 0,
    "presence_penalty": 0
}
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_TEST_BEDROCK")


model = BedrockConverseModel(
    model_name="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    settings=AnthropicModelSettings(**model_settings)
)
mcp_url = os.getenv("MCP_SERVER_URL","http://localhost:8080/sse/")
async def test_pydantic_mcp_bedrock():
    """Test Pydantic AI MCP integration with AWS Bedrock."""
    logger.info("Testing Pydantic AI MCP integration with AWS Bedrock")
    mcp_server = MCPServerSSE(mcp_url)
    
    # Usando Bedrock con Claude 4.5 Sonnet (lanzado septiembre 2025)
    agent = Agent(
        model=model,
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
           - Devuelve el JSON ENRIQUECIDO con splash art
           - Cada campeón debe tener su campo "splash" con la URL
           - NO añadas interpretaciones, solo el JSON enriquecido""",
        mcp_servers=[mcp_server]
    )

    user_query = """Genera el Wrapped 2025 COMPLETO CON SPLASH ART del jugador NamiNami#LAN.
    
    Instrucciones (SIGUE TODOS LOS PASOS):
    
    PASO 1 - Obtener Wrapped:
    Llama get_player_wrapped con estos parámetros:
       - game_name: "Kang Haerin"
       - tag_line: "fox"
       - region: "la1"
       - max_matches: 100  (tardará ~60-90 segundos con rate limiting)
       - year: 2025
    
    PASO 2 - Enriquecer con splash art (OPTIMIZADO):
    Del JSON resultante, extrae TODOS los championId que encuentres.
    Luego llama get_champion_splash_urls pasando los IDs separados por comas.
    Ejemplo: si encuentras championId 103, 222, 157 → llama get_champion_splash_urls("103,222,157")
    
    Esto te devolverá: [{"championId": 103, "name": "Ahri", "splash": "url..."}]
    
    PASO 3 - Combinar datos:
    Toma el JSON del Wrapped y añade SOLO el campo "splash" a cada campeón según su championId.
    
    SALIDA FINAL:
    Devuelve el JSON completo enriquecido con las URLs de splash art.
    NO interpretes, NO resumas, solo devuelve el JSON enriquecido.
    """
    
    async with agent.run_mcp_servers():
        logger.info(f"Executing query with Bedrock: {user_query}")
        result = await agent.run(user_query)
        
        # Parsear y visualizar el resultado
        output = result.output
        
        # Limpiar markdown si existe
        if output.startswith("```json"):
            output = output.replace("```json\n", "").replace("\n```", "").strip()
        elif output.startswith("```"):
            output = output.replace("```\n", "").replace("\n```", "").strip()
        print(output)
        from visualizer import visualize_wrapped
        import json
        print("\n" + visualize_wrapped(output))
        
        # También guardar el JSON raw
        with open("wrapped_output_strands.json", "w") as f:
            json.dump(json.loads(output), f, indent=2)
        logger.info("Wrapped guardado en wrapped_output_strands.json")
async def main():
    await test_pydantic_mcp_bedrock()

if __name__ == "__main__":
    asyncio.run(main())

