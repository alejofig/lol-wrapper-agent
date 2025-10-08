#!/usr/bin/env python3
"""Servidor MCP HTTP para la API de Champion Mastery v4 de Riot Games.

Este servidor expone las herramientas MCP a través de HTTP/SSE en lugar de stdio,
permitiendo su uso con agentes web y clientes HTTP.
"""

import os
import sys
import json
from typing import Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Asegurar que el directorio padre está en el path para importaciones
if __name__ == "__main__":
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))

from mcp.server.fastmcp import FastMCP

try:
    from .client import RiotAPIClient
    from .analytics import analyze_match_history, generate_wrapped_insights, filter_matches_by_year
except ImportError:
    from lol_wrapper.client import RiotAPIClient
    from lol_wrapper.analytics import analyze_match_history, generate_wrapped_insights, filter_matches_by_year

# Cargar variables de entorno
load_dotenv()

# Obtener configuración
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "na1")
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))

if not RIOT_API_KEY:
    raise ValueError(
        "RIOT_API_KEY no encontrada. "
        "Por favor configura tu API key en el archivo .env o como variable de entorno."
    )

# Inicializar FastMCP
mcp = FastMCP("League of Legends Champion Mastery API")

# Cliente global de la API
client = RiotAPIClient(RIOT_API_KEY, DEFAULT_REGION)


def normalize_region(region: Optional[str]) -> str:
    """
    Normaliza la región para asegurar consistencia en todas las herramientas.
    
    Args:
        region: Región opcional provista por el usuario
        
    Returns:
        Región normalizada (nunca None)
    """
    if region is None or region == "":
        return DEFAULT_REGION
    return region.lower().strip()


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
    """
    try:
        region = normalize_region(region)
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
    """
    try:
        region = normalize_region(region)
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
    """
    try:
        region = normalize_region(region)
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
    """
    try:
        region = normalize_region(region)
        
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
    """
    try:
        region = normalize_region(region)
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


# ===== LEAGUE/RANKED API =====

@mcp.tool()
async def get_ranked_info(
    puuid: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene información de ranked (liga) de un jugador por PUUID.
    Incluye tier, división, LP, winrate, etc.
    
    Args:
        puuid: PUUID del jugador (obtener con get_summoner_by_name)
        region: Región del servidor
    
    Returns:
        JSON con información de todas las colas ranked (Solo/Duo, Flex)
    
    Example:
        >>> get_ranked_info("puuid_abc...", "la1")
        [
            {
                "queueType": "RANKED_SOLO_5x5",
                "tier": "DIAMOND",
                "rank": "II",
                "leaguePoints": 45,
                "wins": 123,
                "losses": 98
            }
        ]
    """
    try:
        region = normalize_region(region)
        result = await client.get_league_entries_by_puuid(puuid, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener información de ranked"
        }, indent=2)


@mcp.tool()
async def get_challenger_players(
    queue: str = "RANKED_SOLO_5x5",
    region: Optional[str] = None
) -> str:
    """
    Obtiene la lista de jugadores Challenger.
    
    Args:
        queue: Tipo de cola (RANKED_SOLO_5x5 o RANKED_FLEX_SR)
        region: Región del servidor
    
    Returns:
        JSON con información de la liga Challenger
    """
    try:
        region = normalize_region(region)
        result = await client.get_challenger_league(queue, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener liga Challenger"
        }, indent=2)


@mcp.tool()
async def get_grandmaster_players(
    queue: str = "RANKED_SOLO_5x5",
    region: Optional[str] = None
) -> str:
    """
    Obtiene la lista de jugadores Grandmaster.
    
    Args:
        queue: Tipo de cola (RANKED_SOLO_5x5 o RANKED_FLEX_SR)
        region: Región del servidor
    
    Returns:
        JSON con información de la liga Grandmaster
    """
    try:
        region = normalize_region(region)
        result = await client.get_grandmaster_league(queue, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener liga Grandmaster"
        }, indent=2)


@mcp.tool()
async def get_master_players(
    queue: str = "RANKED_SOLO_5x5",
    region: Optional[str] = None
) -> str:
    """
    Obtiene la lista de jugadores Master.
    
    Args:
        queue: Tipo de cola (RANKED_SOLO_5x5 o RANKED_FLEX_SR)
        region: Región del servidor
    
    Returns:
        JSON con información de la liga Master
    """
    try:
        region = normalize_region(region)
        result = await client.get_master_league(queue, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener liga Master"
        }, indent=2)


# ===== MATCH HISTORY API =====

@mcp.tool()
async def get_match_history(
    puuid: str,
    count: int = 20,
    region: Optional[str] = None
) -> str:
    """
    Obtiene el historial de IDs de partidas de un jugador.
    
    Args:
        puuid: PUUID del jugador
        count: Número de partidas (1-100, default: 20)
        region: Región del servidor
    
    Returns:
        JSON con lista de IDs de partidas
    
    Example:
        >>> get_match_history("puuid_abc", 5, "la1")
        ["LA1_123456", "LA1_123457", ...]
    """
    try:
        region = normalize_region(region)
        
        if count < 1 or count > 100:
            return json.dumps({
                "error": "count debe estar entre 1 y 100",
                "message": "Valor de count inválido"
            }, indent=2)
        
        result = await client.get_match_history(puuid, count, 0, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener historial de partidas"
        }, indent=2)


@mcp.tool()
async def get_match_details(
    match_id: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene detalles completos de una partida específica.
    Incluye stats de todos los jugadores, items, kills, deaths, assists, etc.
    
    Args:
        match_id: ID de la partida (ej: "LA1_123456789")
        region: Región del servidor
    
    Returns:
        JSON con información detallada de la partida
    
    Example:
        >>> get_match_details("LA1_123456789", "la1")
        {
            "metadata": {...},
            "info": {
                "participants": [...],
                "gameMode": "CLASSIC",
                "gameDuration": 1845
            }
        }
    """
    try:
        region = normalize_region(region)
        result = await client.get_match_details(match_id, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": f"Error al obtener detalles de la partida {match_id}"
        }, indent=2)


@mcp.tool()
async def get_match_timeline(
    match_id: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene la timeline minuto a minuto de una partida.
    Incluye eventos como kills, objetivos, farming, etc.
    
    Args:
        match_id: ID de la partida
        region: Región del servidor
    
    Returns:
        JSON con timeline detallada de la partida
    """
    try:
        region = normalize_region(region)
        result = await client.get_match_timeline(match_id, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": f"Error al obtener timeline de la partida {match_id}"
        }, indent=2)


# ===== SPECTATOR/LIVE GAME API =====

@mcp.tool()
async def get_current_game(
    puuid: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene información de la partida en curso de un jugador (si está jugando).
    
    Args:
        puuid: PUUID del jugador
        region: Región del servidor
    
    Returns:
        JSON con información de la partida en curso
    
    Example:
        >>> get_current_game("puuid_abc", "la1")
        {
            "gameMode": "CLASSIC",
            "participants": [...],
            "bannedChampions": [...]
        }
    """
    try:
        region = normalize_region(region)
        result = await client.get_current_game(puuid, region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "El jugador no está en una partida o error al obtener información"
        }, indent=2)


@mcp.tool()
async def get_featured_games(
    region: Optional[str] = None
) -> str:
    """
    Obtiene partidas destacadas actualmente en curso.
    Útil para encontrar partidas de alto nivel o streamers.
    
    Args:
        region: Región del servidor
    
    Returns:
        JSON con lista de partidas destacadas
    """
    try:
        region = normalize_region(region)
        result = await client.get_featured_games(region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener partidas destacadas"
        }, indent=2)


# ===== CHAMPION ROTATION API =====

@mcp.tool()
async def get_free_champion_rotation(
    region: Optional[str] = None
) -> str:
    """
    Obtiene la rotación de campeones gratuitos de esta semana.
    
    Args:
        region: Región del servidor
    
    Returns:
        JSON con IDs de campeones gratuitos
    
    Example:
        >>> get_free_champion_rotation("la1")
        {
            "freeChampionIds": [1, 2, 3, 4, ...],
            "freeChampionIdsForNewPlayers": [18, 21, 22, ...],
            "maxNewPlayerLevel": 10
        }
    """
    try:
        region = normalize_region(region)
        result = await client.get_champion_rotations(region)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener rotación de campeones"
        }, indent=2)


# ===== WRAPPED / ANALYTICS API =====

@mcp.tool()
async def get_player_profile_complete(
    game_name: str,
    tag_line: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene el perfil completo de un jugador: info básica + ranked + maestrías.
    Esta es la herramienta principal para iniciar un Wrapped.
    
    Args:
        game_name: Nombre del invocador
        tag_line: Tag del invocador
        region: Región del servidor
    
    Returns:
        JSON con perfil completo del jugador
    
    Example:
        >>> get_player_profile_complete("NamiNami", "LAN", "la1")
        {
            "account": {...},
            "summoner": {...},
            "ranked": [...],
            "mastery_score": 123,
            "top_masteries": [...]
        }
    """
    try:
        # Normalizar región
        region = normalize_region(region)
        
        # 1. Obtener info de cuenta (usa cluster regional automáticamente)
        account = await client.get_summoner_by_name(game_name, tag_line, region)
        puuid = account["puuid"]
        
        # 2. Obtener info de summoner (DEBE usar la región específica)
        summoner = await client.get_summoner_by_puuid(puuid, region)
        
        # 3. Obtener ranked info (ahora usa PUUID directamente)
        ranked_info = await client.get_league_entries_by_puuid(puuid, region)
        
        # 4. Obtener maestría (DEBE usar la región específica)
        mastery_score = await client.get_mastery_score(puuid, region)
        top_masteries = await client.get_top_champion_masteries(puuid, 10, region)
        
        profile = {
            "account": account,
            "summoner": summoner,
            "ranked": ranked_info,
            "mastery_score": mastery_score,
            "top_masteries": top_masteries
        }
        
        return json.dumps(profile, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener perfil completo del jugador"
        }, indent=2)


@mcp.tool()
async def get_player_wrapped(
    game_name: str,
    tag_line: str,
    region: Optional[str] = None,
    match_count: int = 100,
    year: Optional[int] = None
) -> str:
    """
    🎁 HERRAMIENTA PRINCIPAL PARA WRAPPED 🎁
    
    Genera un "Wrapped del Año" completo de un jugador con todas sus estadísticas,
    campeones favoritos, mejores partidas y más.
    
    Esta herramienta obtiene y analiza hasta 100 partidas del jugador para generar
    estadísticas agregadas perfectas para una web app de Wrapped.
    
    Args:
        game_name: Nombre del invocador
        tag_line: Tag del invocador (ej: LAN, NA1, KR1)
        region: Región del servidor (ej: la1, na1, kr)
        match_count: Número de partidas a analizar (1-100, default: 100)
        year: Año a analizar (None = año actual)
    
    Returns:
        JSON con Wrapped completo incluyendo:
        - Perfil del jugador
        - Estadísticas generales (wins, losses, winrate, KDA)
        - Top campeones jugados
        - Roles preferidos
        - Mejor y peor partida
        - Multikills (pentakills, quadrakills)
        - Insights y frases motivacionales
        - Stats detallados por campeón
    
    Example:
        >>> get_player_wrapped("Faker", "KR1", "kr", 100, 2024)
        {
            "player": {...},
            "year": 2024,
            "statistics": {
                "total_games": 150,
                "wins": 95,
                "losses": 55,
                "winrate": 63.33,
                "avg_kda": 4.5,
                ...
            },
            "insights": ["Jugaste 150 partidas...", ...],
            ...
        }
    """
    try:
        # Normalizar región
        region = normalize_region(region)
        match_count = min(max(match_count, 1), 100)  # Límite 1-100
        
        # 1. Obtener perfil completo (TODAS las llamadas usan la misma región)
        account = await client.get_summoner_by_name(game_name, tag_line, region)
        puuid = account["puuid"]
        
        summoner = await client.get_summoner_by_puuid(puuid, region)
        
        # Obtener ranked info (ahora usa PUUID directamente)
        ranked_info = await client.get_league_entries_by_puuid(puuid, region)
        mastery_score = await client.get_mastery_score(puuid, region)
        top_masteries = await client.get_top_champion_masteries(puuid, 5, region)
        
        # 2. Obtener historial de partidas
        match_ids = await client.get_match_history(puuid, match_count, 0, region)
        
        # 3. Filtrar por año si se especificó
        if year:
            match_ids = filter_matches_by_year(match_ids, year)
        
        # 4. Obtener detalles de todas las partidas (esto puede tomar tiempo)
        matches = []
        for match_id in match_ids[:match_count]:  # Limitar para evitar timeouts
            try:
                match_detail = await client.get_match_details(match_id, region)
                matches.append(match_detail)
            except Exception as e:
                # Continuar si alguna partida falla
                continue
        
        # 5. Analizar estadísticas
        statistics = analyze_match_history(matches, puuid)
        
        # 6. Generar insights
        insights = generate_wrapped_insights(statistics)
        
        # 7. Construir respuesta completa
        wrapped = {
            "player": {
                "game_name": account["gameName"],
                "tag_line": account["tagLine"],
                "puuid": puuid,
                "summoner_level": summoner.get("summonerLevel", 0),
                "profile_icon_id": summoner.get("profileIconId", 0),
                "mastery_score": mastery_score
            },
            "year": year if year else "current",
            "ranked": ranked_info,
            "top_masteries": top_masteries,
            "statistics": statistics,
            "insights": insights,
            "matches_analyzed": len(matches),
            "generated_at": json.dumps(datetime.now().isoformat())
        }
        
        return json.dumps(wrapped, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al generar Wrapped del jugador",
            "details": "Asegúrate de que el jugador existe y tiene partidas en el año especificado"
        }, indent=2)


@mcp.tool()
async def get_detailed_match_analysis(
    match_id: str,
    puuid: str,
    region: Optional[str] = None
) -> str:
    """
    Obtiene análisis detallado de una partida específica para un jugador.
    Útil para mostrar "highlights" en el Wrapped.
    
    Args:
        match_id: ID de la partida
        puuid: PUUID del jugador
        region: Región del servidor
    
    Returns:
        JSON con análisis detallado de la partida
    
    Example:
        >>> get_detailed_match_analysis("LA1_123456", "puuid_abc", "la1")
        {
            "match_id": "LA1_123456",
            "champion": "Yasuo",
            "result": "Victory",
            "kda": 4.5,
            "performance": {
                "kills": 9,
                "deaths": 2,
                "assists": 15,
                ...
            },
            ...
        }
    """
    try:
        # Normalizar región
        region = normalize_region(region)
        
        # Obtener detalles de la partida
        match = await client.get_match_details(match_id, region)
        
        # Encontrar al jugador
        player_data = None
        for participant in match["info"]["participants"]:
            if participant["puuid"] == puuid:
                player_data = participant
                break
        
        if not player_data:
            return json.dumps({
                "error": "Jugador no encontrado en la partida"
            }, indent=2)
        
        # Extraer información relevante
        from lol_wrapper.analytics import calculate_kda
        
        analysis = {
            "match_id": match_id,
            "game_mode": match["info"]["gameMode"],
            "game_duration_minutes": match["info"]["gameDuration"] // 60,
            "champion": player_data["championName"],
            "result": "Victory" if player_data["win"] else "Defeat",
            "performance": {
                "kills": player_data["kills"],
                "deaths": player_data["deaths"],
                "assists": player_data["assists"],
                "kda": calculate_kda(
                    player_data["kills"],
                    player_data["deaths"],
                    player_data["assists"]
                ),
                "damage_dealt": player_data["totalDamageDealtToChampions"],
                "damage_taken": player_data["totalDamageTaken"],
                "gold_earned": player_data["goldEarned"],
                "cs": player_data["totalMinionsKilled"] + player_data.get("neutralMinionsKilled", 0),
                "vision_score": player_data.get("visionScore", 0)
            },
            "achievements": {
                "pentakills": player_data.get("pentaKills", 0),
                "quadrakills": player_data.get("quadraKills", 0),
                "triplekills": player_data.get("tripleKills", 0),
                "doublekills": player_data.get("doubleKills", 0),
                "first_blood": player_data.get("firstBloodKill", False),
                "first_tower": player_data.get("firstTowerKill", False)
            },
            "items": [
                player_data.get(f"item{i}", 0)
                for i in range(7)
                if player_data.get(f"item{i}", 0) > 0
            ]
        }
        
        return json.dumps(analysis, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": f"Error al analizar la partida {match_id}"
        }, indent=2)


def main():
    """Punto de entrada principal para el servidor MCP SSE."""
    import asyncio
    
    async def cleanup():
        """Limpieza al cerrar el servidor."""
        await client.close()
    
    # Registrar limpieza
    import atexit
    atexit.register(lambda: asyncio.run(cleanup()))
    
    # Iniciar servidor MCP con transporte SSE
    print(f"🚀 Iniciando servidor MCP con SSE...")
    print(f"   Transporte: Server-Sent Events (SSE)")
    print(f"   Puerto por defecto: 8000")
    print(f"\n📚 Herramientas MCP disponibles (20 tools):")
    print(f"\n   🎯 Summoner & Account:")
    print(f"      - get_summoner_by_name")
    print(f"      - get_available_regions")
    print(f"\n   ⭐ Champion Mastery:")
    print(f"      - get_champion_masteries")
    print(f"      - get_champion_mastery")
    print(f"      - get_top_champion_masteries")
    print(f"      - get_mastery_score")
    print(f"\n   🏆 Ranked/League:")
    print(f"      - get_ranked_info")
    print(f"      - get_challenger_players")
    print(f"      - get_grandmaster_players")
    print(f"      - get_master_players")
    print(f"\n   📜 Match History:")
    print(f"      - get_match_history")
    print(f"      - get_match_details")
    print(f"      - get_match_timeline")
    print(f"\n   🎮 Live Game:")
    print(f"      - get_current_game")
    print(f"      - get_featured_games")
    print(f"\n   🔄 Champion Rotation:")
    print(f"      - get_free_champion_rotation")
    print(f"\n   🎁 WRAPPED (Para tu web app):")
    print(f"      - get_player_wrapped ⭐ PRINCIPAL")
    print(f"      - get_player_profile_complete")
    print(f"      - get_detailed_match_analysis")
    print(f"\n✅ Servidor MCP SSE listo. Presiona Ctrl+C para detener.")
    print(f"\n💡 Para usar con un agente MCP, configura:")
    print(f'   "transport": "sse"')
    print(f'   "url": "http://localhost:8000/sse"')
    print(f"\n🎯 Para el Wrapped usa: get_player_wrapped(game_name, tag_line, region)\n")
    
    # Iniciar servidor MCP en modo SSE
    # FastMCP manejará el servidor HTTP internamente
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()

