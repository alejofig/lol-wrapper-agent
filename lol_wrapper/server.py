#!/usr/bin/env python3
"""Servidor MCP para la API de Champion Mastery v4 de Riot Games."""

import os
import sys
import json
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Asegurar que el directorio padre está en el path para importaciones
if __name__ == "__main__":
    # Añadir el directorio padre al path cuando se ejecuta directamente
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))

from mcp.server.fastmcp import FastMCP

# Intentar importación relativa primero, luego absoluta
try:
    from .client import RiotAPIClient
except ImportError:
    from lol_wrapper.client import RiotAPIClient

# Cargar variables de entorno
load_dotenv()

# Obtener configuración
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "na1")

if not RIOT_API_KEY:
    raise ValueError(
        "RIOT_API_KEY no encontrada. "
        "Por favor configura tu API key en el archivo .env o como variable de entorno."
    )

# Inicializar FastMCP
mcp = FastMCP("League of Legends Champion Mastery API")

# Cliente global de la API
client = RiotAPIClient(RIOT_API_KEY, DEFAULT_REGION)


@mcp.tool()
async def get_summoner_by_name(
    game_name: str,
    tag_line: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene información de un invocador por su nombre de juego y tag.
    Útil para obtener el PUUID necesario para otras operaciones.
    
    Args:
        game_name: Nombre del invocador (ej: "Faker")
        tag_line: Tag del invocador (ej: "KR1", "NA1", "LAN")
        region: Región del servidor (br1, eun1, euw1, jp1, kr, la1, la2, na1, oc1, ph2, ru, sg2, th2, tr1, tw2, vn2)
    
    Returns:
        JSON con información del invocador incluyendo puuid, gameName y tagLine
    
    Example:
        >>> get_summoner_by_name("Faker", "KR1", "kr")
        {
            "puuid": "...",
            "gameName": "Faker",
            "tagLine": "KR1"
        }
    """
    try:
        result = await client.get_summoner_by_name(game_name, tag_line, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener información del invocador"
        }, indent=2)


@mcp.tool()
async def get_champion_masteries(
    puuid: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene todas las maestrías de campeones de un jugador.
    Retorna información detallada de cada campeón incluyendo nivel, puntos y tokens.
    
    Args:
        puuid: PUUID del jugador (obtener con get_summoner_by_name)
        region: Región del servidor (opcional, usa la región por defecto si no se especifica)
    
    Returns:
        JSON con lista de todas las maestrías de campeones del jugador
    
    Example:
        >>> get_champion_masteries("abc123...", "na1")
        [
            {
                "championId": 157,
                "championLevel": 7,
                "championPoints": 234567,
                "lastPlayTime": 1234567890,
                "championPointsSinceLastLevel": 21600,
                "championPointsUntilNextLevel": 0,
                "tokensEarned": 2
            },
            ...
        ]
    """
    try:
        result = await client.get_champion_masteries(puuid, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener maestrías de campeones"
        }, indent=2)


@mcp.tool()
async def get_champion_mastery(
    puuid: str,
    champion_id: int,
    region: Optional[str] = None
) -> str:
    """
    Obtiene la maestría de un campeón específico para un jugador.
    
    Args:
        puuid: PUUID del jugador
        champion_id: ID del campeón (ej: 157 para Yasuo, 51 para Caitlyn)
        region: Región del servidor
    
    Returns:
        JSON con información de maestría del campeón específico
    
    Example:
        >>> get_champion_mastery("abc123...", 157, "na1")
        {
            "championId": 157,
            "championLevel": 7,
            "championPoints": 234567,
            "lastPlayTime": 1234567890,
            "championPointsSinceLastLevel": 21600,
            "championPointsUntilNextLevel": 0,
            "tokensEarned": 2
        }
    """
    try:
        result = await client.get_champion_mastery(puuid, champion_id, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": f"Error al obtener maestría del campeón {champion_id}"
        }, indent=2)


@mcp.tool()
async def get_top_champion_masteries(
    puuid: str,
    count: int = 3,
    region: Optional[str] = None
) -> str:
    """
    Obtiene las top maestrías de campeones de un jugador.
    Útil para ver los campeones más jugados/dominados.
    
    Args:
        puuid: PUUID del jugador
        count: Número de campeones a retornar (1-10, default: 3)
        region: Región del servidor
    
    Returns:
        JSON con lista de top maestrías ordenadas por puntos
    
    Example:
        >>> get_top_champion_masteries("abc123...", 5, "na1")
        [
            {
                "championId": 157,
                "championLevel": 7,
                "championPoints": 234567,
                ...
            },
            {
                "championId": 51,
                "championLevel": 6,
                "championPoints": 123456,
                ...
            },
            ...
        ]
    """
    try:
        if count < 1 or count > 10:
            return json.dumps({
                "error": "count debe estar entre 1 y 10",
                "message": "Valor de count inválido"
            }, indent=2)
        
        result = await client.get_top_champion_masteries(puuid, count, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener top maestrías"
        }, indent=2)


@mcp.tool()
async def get_mastery_score(
    puuid: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene la puntuación total de maestría de un jugador.
    Esta es la suma de todos los niveles de maestría de todos los campeones.
    
    Args:
        puuid: PUUID del jugador
        region: Región del servidor
    
    Returns:
        JSON con la puntuación total de maestría
    
    Example:
        >>> get_mastery_score("abc123...", "na1")
        {
            "totalMasteryScore": 342
        }
    """
    try:
        result = await client.get_mastery_score(puuid, region)
        return json.dumps({
            "totalMasteryScore": result
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener puntuación de maestría"
        }, indent=2)


@mcp.tool()
async def get_available_regions() -> str:
    """
    Lista todas las regiones disponibles para consultar la API.
    
    Returns:
        JSON con lista de regiones disponibles y sus clusters regionales
    
    Example:
        >>> get_available_regions()
        {
            "platforms": ["br1", "eun1", "euw1", ...],
            "clusters": {
                "americas": ["br1", "la1", "la2", "na1", "oc1"],
                "asia": ["kr", "jp1"],
                "europe": ["eun1", "euw1", "tr1", "ru"],
                "sea": ["ph2", "sg2", "th2", "tw2", "vn2"]
            }
        }
    """
    clusters = {
        "americas": ["br1", "la1", "la2", "na1", "oc1"],
        "asia": ["kr", "jp1"],
        "europe": ["eun1", "euw1", "tr1", "ru"],
        "sea": ["ph2", "sg2", "th2", "tw2", "vn2"]
    }
    
    return json.dumps({
        "platforms": list(RiotAPIClient.PLATFORMS.keys()),
        "clusters": clusters,
        "default_region": DEFAULT_REGION
    }, indent=2, ensure_ascii=False)


def main():
    """Punto de entrada principal para el servidor MCP."""
    import asyncio
    
    async def cleanup():
        """Limpieza al cerrar el servidor."""
        await client.close()
    
    # Registrar limpieza
    import atexit
    atexit.register(lambda: asyncio.run(cleanup()))
    
    # Iniciar servidor
    mcp.run()


if __name__ == "__main__":
    main()

