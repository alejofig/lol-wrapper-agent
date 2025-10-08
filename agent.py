import asyncio
import logging
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE #
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_TEST")


async def test_pydantic_mcp():
    """Test Pydantic AI MCP integration with sanitized server."""
    logger.info("Testing Pydantic AI MCP integration")
    mcp_server = MCPServerSSE(url="http://localhost:8000/sse/") # Change to your MCP endpoint
    
    agent = Agent(
        "openai:gpt-4o",
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
        
        3. HERRAMIENTA PRINCIPAL:
           - USA get_player_wrapped para obtener TODO el Wrapped en una sola llamada
           - Esta herramienta ya hace TODAS las peticiones necesarias
           - NO necesitas llamar get_summoner_by_name primero
        
        4. SALIDA:
           - Devuelve el JSON resultante sin modificar
           - NO añadas interpretaciones ni comentarios extras""",
        mcp_servers=[mcp_server]
    )

    user_query = """Genera el Wrapped 2025 del jugador Kang Haerin#fox.
    
    Instrucciones:
    1. Llama get_player_wrapped con estos parámetros EXACTOS:
       - game_name: "Kang Haerin"
       - tag_line: "fox"
       - region: "la1"
       - match_count: 20
       - year: 2025
    
    2. Devuelve el JSON completo que obtengas
    3. NO interpretes los datos, solo devuélvelos
    """
    
    async with agent.run_mcp_servers():
        logger.info(f"Executing query: {user_query}")
        result = await agent.run(user_query)
        
        # Parsear y visualizar el resultado
        output = result.output
        
        # Limpiar markdown si existe
        if output.startswith("```json"):
            output = output.replace("```json\n", "").replace("\n```", "").strip()
        elif output.startswith("```"):
            output = output.replace("```\n", "").replace("\n```", "").strip()
        
        # Visualizar
        from visualizer import visualize_wrapped
        print("\n" + visualize_wrapped(output))
        
        # También guardar el JSON raw
        import json
        with open("wrapped_output.json", "w") as f:
            json.dump(json.loads(output), f, indent=2)
        logger.info("Wrapped guardado en wrapped_output.json")

async def main():
    await test_pydantic_mcp()

if __name__ == "__main__":
    asyncio.run(main())