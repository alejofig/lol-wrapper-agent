import asyncio
import logging
import json
from mcp.client.sse import sse_client
from strands import Agent
from strands.tools.mcp import MCPClient
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_TEST_STRANDS")


async def test_strands_mcp():
    """Test Strands MCP integration with sanitized server."""
    logger.info("Testing Strands MCP integration")
    
    # Connect to an MCP server using SSE transport
    sse_mcp_client = MCPClient(lambda: sse_client("http://localhost:8000/sse"))
    
    # Create an agent with MCP tools
    with sse_mcp_client:
        # Get the tools from the MCP server
        tools = sse_mcp_client.list_tools_sync()
        
        # Create an agent with these tools
        agent = Agent(
            tools=tools,
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
           - NO añadas interpretaciones ni comentarios extras"""
        )
        
        user_query = """Genera el Wrapped 2025 del jugador NamiNami#LAN.
    
        Instrucciones:
        1. Llama get_player_wrapped con estos parámetros EXACTOS:
           - game_name: "NamiNami"
           - tag_line: "LAN"
           - region: "la1"
           - max_matches: 100  (con rate limiting, tardará ~60-90 segundos)
           - year: 2025
        
        2. Devuelve el JSON completo que obtengas
        3. NO interpretes los datos, solo devuélvelos
        """
        
        logger.info(f"Executing query: {user_query}")
        result = agent(user_query)
        
        # Parsear y visualizar el resultado
        output = result.message
        print(output)
        # Si el resultado es un diccionario, extraer el contenido del texto
        if isinstance(output, dict):
            # En strands, el mensaje puede venir en diferentes formatos
            if 'content' in output:
                output = output['content']
            elif 'text' in output:
                output = output['text']
            else:
                # Si no encontramos el campo esperado, usar el diccionario completo como string
                output = str(output)
        
        # Limpiar markdown si existe
        if isinstance(output, str):
            if output.startswith("```json"):
                output = output.replace("```json\n", "").replace("\n```", "").strip()
            elif output.startswith("```"):
                output = output.replace("```\n", "").replace("\n```", "").strip()
        print(output)
        # Visualizar
        from visualizer import visualize_wrapped
        print("\n" + visualize_wrapped(output))
        
        # También guardar el JSON raw
        with open("wrapped_output_strands.json", "w") as f:
            json.dump(json.loads(output), f, indent=2)
        logger.info("Wrapped guardado en wrapped_output_strands.json")


async def main():
    await test_strands_mcp()


if __name__ == "__main__":
    asyncio.run(main())