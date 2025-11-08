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
    from .analytics import (
        analyze_match_history, 
        generate_wrapped_insights,
        analyze_challenges,
        generate_challenge_insights
    )
    from .data_dragon import DataDragonClient
except ImportError:
    from lol_wrapper.client import RiotAPIClient
    from lol_wrapper.analytics import (
        analyze_match_history, 
        generate_wrapped_insights,
        analyze_challenges,
        generate_challenge_insights
    )
    from lol_wrapper.data_dragon import DataDragonClient

# Cargar variables de entorno
load_dotenv()

# Obtener configuración
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "na1")
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("PORT", "8080"))

if not RIOT_API_KEY:
    raise ValueError(
        "RIOT_API_KEY no encontrada. "
        "Por favor configura tu API key en el archivo .env o como variable de entorno."
    )

# Inicializar FastMCP
mcp = FastMCP("League of Legends Champion Mastery API", host=HTTP_HOST, port=HTTP_PORT)

# Cliente global de la API
client = RiotAPIClient(RIOT_API_KEY, DEFAULT_REGION)

# Cliente de Data Dragon (CDN de assets - no consume rate limits)
ddragon = DataDragonClient()


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


# ===== CHALLENGES API =====

@mcp.tool()
async def get_player_challenges(
    game_name: str,
    tag_line: str,
    region: Optional[str] = None
) -> str:
    """
    🏆 Obtiene todos los desafíos y logros de un jugador.
    
    Los desafíos son logros especiales de League of Legends que muestran
    el progreso del jugador en diferentes categorías como:
    - Veteranía (tiempo jugado, experiencia)
    - Colección (campeones, skins)
    - Experticia (maestría mecánica)
    - Trabajo en Equipo (cooperación)
    - Imaginación (creatividad en el juego)
    
    Args:
        game_name: Nombre del invocador
        tag_line: Tag del invocador (ej: LAN, NA1, KR1)
        region: Región del servidor
    
    Returns:
        JSON con:
        - Puntos totales de desafíos
        - Nivel global
        - Top 5 desafíos por percentil
        - Desglose por categoría
        - Logros en percentiles altos (top 1%, 5%, 10%)
        - Conteo de desafíos por nivel
        - Insights motivacionales
    
    Example:
        >>> get_player_challenges("Faker", "KR1", "kr")
        {
            "challenges": {
                "total_points": 15000,
                "total_level": "MASTER",
                "top_challenges": [...],
                "percentile_achievements": [
                    {
                        "challenge_id": 101101,
                        "level": "GRANDMASTER",
                        "percentile": 0.99,
                        "tier": "top_1_percent"
                    }
                ],
                "category_breakdown": {...},
                "level_counts": {...}
            },
            "insights": [
                "🏆 Acumulaste 15,000 puntos de desafíos!",
                "⭐ ¡INCREÍBLE! Estás en el TOP 1% en 3 desafío(s)",
                ...
            ]
        }
    """
    try:
        region = normalize_region(region)
        
        # 1. Obtener PUUID del jugador
        player_context = f"{game_name}-{tag_line}"
        account = await client.get_summoner_by_name(game_name, tag_line, region)
        puuid = account["puuid"]
        
        # 2. Obtener datos de desafíos
        challenges_data = await client.get_player_challenges(puuid, region, s3_context=player_context)
        
        # 3. Analizar desafíos
        challenge_analysis = analyze_challenges(challenges_data)
        
        # 4. Generar insights
        challenge_insights = generate_challenge_insights(challenge_analysis)
        
        # 5. Construir respuesta
        result = {
            "player": {
                "game_name": account["gameName"],
                "tag_line": account["tagLine"],
                "puuid": puuid
            },
            "challenges": challenge_analysis,
            "insights": challenge_insights
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener desafíos del jugador",
            "details": "Verifica que el jugador existe y la región es correcta"
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
        player_context = f"{game_name}-{tag_line}"
        account = await client.get_summoner_by_name(game_name, tag_line, region)
        puuid = account["puuid"]
        
        # 2. Obtener info de summoner (DEBE usar la región específica)
        summoner = await client.get_summoner_by_puuid(puuid, region, s3_context=player_context)
        
        # 3. Obtener ranked info (ahora usa PUUID directamente)
        ranked_info = await client.get_league_entries_by_puuid(puuid, region, s3_context=player_context)
        
        # 4. Obtener maestría (DEBE usar la región específica)
        mastery_score = await client.get_mastery_score(puuid, region, s3_context=player_context)
        top_masteries = await client.get_top_champion_masteries(puuid, 10, region, s3_context=player_context)
        
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
    max_matches: int = 100,
    year: int = 2025
) -> str:
    """
    🎁 HERRAMIENTA PRINCIPAL PARA WRAPPED 🎁
    
    Genera un "Wrapped del Año" completo de un jugador con todas sus estadísticas,
    campeones favoritos, mejores partidas y más.
    
    Esta herramienta obtiene y analiza partidas del jugador con rate limiting automático
    para respetar los límites de la API de Riot (20 req/s, 100 req/2min).
    
    Args:
        game_name: Nombre del invocador
        tag_line: Tag del invocador (ej: LAN, NA1, KR1)
        region: Región del servidor (ej: la1, na1, kr)
        max_matches: Máximo de partidas a analizar (default: 100)
                     NOTA: Con Development Key, ~100 partidas toman ~60-90 segundos
                     debido a rate limiting. Aumentar con precaución.
        year: Año a analizar (default: 2025). Usa 0 para TODAS las partidas sin filtrar
    
    Returns:
        JSON con Wrapped completo incluyendo:
        - Perfil del jugador
        - Estadísticas generales (wins, losses, winrate, KDA)
        - Top campeones jugados
        - Roles preferidos
        - Mejor y peor partida
        - Multikills (pentakills, quadrakills)
        - 🏆 Desafíos y logros (puntos, percentiles, badges)
        - Insights y frases motivacionales (partidas + desafíos)
        - Stats detallados por campeón
        - total_matches_in_year: Total EXACTO de partidas jugadas en el año
        - matches_analyzed: Partidas que se analizaron con detalles (limitadas por max_matches)
    
    Example:
        >>> get_player_wrapped("Faker", "KR1", "kr", 5, 2025)
        {
            "player": {...},
            "year": 2025,
            "total_matches_in_year": 342,  # Jugó 342 partidas en total en 2025
            "matches_analyzed": 5,         # Solo analizamos las primeras 5
            "statistics": {
                "total_games": 5,  # Stats basadas solo en las 5 analizadas
                ...
            }
        }
        
        Nota: Primero obtenemos TODOS los IDs para contar el total exacto,
        luego solo analizamos (obtener detalles) las primeras max_matches.
    """
    try:
        # Normalizar región
        region = normalize_region(region)
        max_matches = max(max_matches, 1)  # Mínimo 1
        
        # 1. Obtener perfil completo (TODAS las llamadas usan la misma región)
        player_context = f"{game_name}-{tag_line}"
        account = await client.get_summoner_by_name(game_name, tag_line, region)
        puuid = account["puuid"]
        
        summoner = await client.get_summoner_by_puuid(puuid, region, s3_context=player_context)
        
        # Obtener ranked info (ahora usa PUUID directamente)
        ranked_info = await client.get_league_entries_by_puuid(puuid, region, s3_context=player_context)
        mastery_score = await client.get_mastery_score(puuid, region, s3_context=player_context)
        top_masteries = await client.get_top_champion_masteries(puuid, 5, region, s3_context=player_context)
        
        # 2. Calcular filtros de tiempo si se especifica año
        start_time = None
        end_time = None
        if year and year > 0:
            # Convertir a epoch seconds (Riot API usa segundos, no ms)
            start_time = int(datetime(year, 1, 1).timestamp())
            end_time = int(datetime(year + 1, 1, 1).timestamp())
        
        # 3. Obtener TODOS los IDs de partidas del año (para saber el total exacto)
        all_match_ids = []
        batch_size = 100  # Máximo por request de Riot
        offset = 0
        
        # Paginar hasta obtener TODOS los IDs del año
        while True:
            batch = await client.get_match_history(
                puuid, 
                count=batch_size,
                start=offset,
                region=region,
                start_time=start_time,
                end_time=end_time,
                s3_context=player_context
            )
            
            if not batch:
                # No hay más partidas
                break
            
            all_match_ids.extend(batch)
            offset += len(batch)
            
            # Si el batch retornó menos de 100, llegamos al final
            if len(batch) < batch_size:
                break
        
        # Total exacto de partidas del año
        total_matches_in_year = len(all_match_ids)
        
        # Solo analizar las primeras max_matches partidas
        match_ids = all_match_ids[:max_matches]
        
        # 4. Obtener detalles de las partidas a analizar (esto puede tomar tiempo)
        matches = []
        for match_id in match_ids:
            try:
                match_detail = await client.get_match_details(match_id, region, s3_context=player_context)
                matches.append(match_detail)
            except Exception:
                # Continuar si alguna partida falla
                continue
        
        # 5. Analizar estadísticas
        statistics = analyze_match_history(matches, puuid)
        
        # 6. Generar insights de partidas (con info de total vs analizadas)
        insights = generate_wrapped_insights(
            statistics,
            total_matches_in_year=total_matches_in_year,
            matches_analyzed=len(matches)
        )
        
        # 7. Obtener y analizar desafíos
        challenges_data = None
        challenge_analysis = None
        challenge_insights = []
        try:
            challenges_data = await client.get_player_challenges(puuid, region, s3_context=player_context)
            challenge_analysis = analyze_challenges(challenges_data)
            challenge_insights = generate_challenge_insights(challenge_analysis)
        except Exception:
            # Si falla, continuar sin desafíos
            pass
        
        # 8. Combinar insights
        all_insights = insights + challenge_insights
        
        # 9. Construir respuesta completa
        wrapped = {
            "player": {
                "game_name": account["gameName"],
                "tag_line": account["tagLine"],
                "puuid": puuid,
                "summoner_level": summoner.get("summonerLevel", 0),
                "profile_icon_id": summoner.get("profileIconId", 0),
                "mastery_score": mastery_score
            },
            "year": year,
            "ranked": ranked_info,
            "top_masteries": top_masteries,
            "statistics": statistics,
            "challenges": challenge_analysis,
            "insights": all_insights,
            "total_matches_in_year": total_matches_in_year,  # Total de partidas en el año
            "matches_analyzed": len(matches),  # Partidas realmente analizadas (limitadas por max_matches)
            "generated_at": json.dumps(datetime.now().isoformat())
        }
        
        return json.dumps(wrapped, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al generar Wrapped del jugador",
            "details": f"Asegúrate de que el jugador existe y tiene partidas en {year}"
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


# ===== DATA DRAGON / IMAGES API =====

@mcp.tool()
async def get_champion_splash_urls(champion_ids: str) -> str:
    """
    🖼️ OPTIMIZADO: Obtiene las URLs de splash art para múltiples campeones en una sola llamada.
    
    Esta herramienta es MUY EFICIENTE porque:
    - NO consume rate limits de Riot API (usa CDN público)
    - Procesa múltiples campeones simultáneamente
    - Retorna URLs directas listas para usar
    
    Args:
        champion_ids: IDs de campeones separados por comas (ej: "103,222,157")
    
    Returns:
        JSON con array de objetos {championId, name, splash}
    
    Example:
        >>> get_champion_splash_urls("103,222,157")
        [
            {
                "championId": 103,
                "name": "Ahri",
                "splash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ahri_0.jpg"
            },
            {
                "championId": 222,
                "name": "Jinx",
                "splash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Jinx_0.jpg"
            }
        ]
    """
    try:
        # Parsear IDs
        ids_list = [int(id.strip()) for id in champion_ids.split(',') if id.strip()]
        
        # Obtener splash URLs
        splash_urls = await ddragon.get_champion_splash_urls(ids_list)
        
        return json.dumps(splash_urls, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener splash URLs de campeones"
        }, indent=2)


@mcp.tool()
async def get_champion_images(champion_id: int) -> str:
    """
    Obtiene todas las imágenes disponibles de un campeón específico.
    
    Args:
        champion_id: ID del campeón
    
    Returns:
        JSON con URLs de splash, square, loading, y passive
    """
    try:
        images = await ddragon.get_champion_images(champion_id)
        return json.dumps(images, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": f"Error al obtener imágenes del campeón {champion_id}"
        }, indent=2)


@mcp.tool()
async def get_multiple_champion_images(champion_ids: str) -> str:
    """
    Obtiene imágenes de múltiples campeones.
    Similar a get_champion_splash_urls pero retorna MÁS información (square, loading, etc).
    
    Args:
        champion_ids: IDs separados por comas
    
    Returns:
        JSON con array de objetos con todas las imágenes por campeón
    """
    try:
        ids_list = [int(id.strip()) for id in champion_ids.split(',') if id.strip()]
        
        results = []
        for champ_id in ids_list:
            try:
                images = await ddragon.get_champion_images(champ_id)
                results.append(images)
            except Exception:
                continue
        
        return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener imágenes de campeones"
        }, indent=2)


@mcp.tool()
async def get_champion_data_with_images(champion_ids: str) -> str:
    """
    Obtiene datos completos de campeones incluyendo imágenes.
    Combina información de nombre, título, tags, stats E imágenes.
    
    Args:
        champion_ids: IDs separados por comas
    
    Returns:
        JSON con datos completos + imágenes
    """
    try:
        ids_list = [int(id.strip()) for id in champion_ids.split(',') if id.strip()]
        
        # Obtener datos de campeones
        champion_data = await ddragon.get_champion_data()
        
        results = []
        for champ_id in ids_list:
            # Buscar campeón por ID
            for champ_key, champ_info in champion_data.items():
                if int(champ_info['key']) == champ_id:
                    # Agregar imágenes
                    try:
                        images = await ddragon.get_champion_images(champ_id)
                        champ_info['images'] = images
                    except Exception:
                        pass
                    
                    results.append(champ_info)
                    break
        
        return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener datos de campeones con imágenes"
        }, indent=2)


@mcp.tool()
async def get_profile_icon_url(icon_id: int) -> str:
    """
    Obtiene la URL del icono de perfil de un jugador.
    
    Args:
        icon_id: ID del icono de perfil
    
    Returns:
        JSON con la URL del icono
    """
    try:
        url = await ddragon.get_profile_icon_url(icon_id)
        return json.dumps({
            "icon_id": icon_id,
            "url": url
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": f"Error al obtener URL del icono {icon_id}"
        }, indent=2)


@mcp.tool()
async def get_latest_version() -> str:
    """
    Obtiene la última versión de Data Dragon (útil para construir URLs manualmente).
    
    Returns:
        JSON con la versión actual
    """
    try:
        version = await ddragon.get_latest_version()
        return json.dumps({
            "version": version,
            "base_url": f"https://ddragon.leagueoflegends.com/cdn/{version}"
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Error al obtener versión de Data Dragon"
        }, indent=2)


def main():
    """Punto de entrada principal para el servidor MCP SSE."""
    # No necesitamos async cleanup para el servidor SSE síncrono
    
    # Iniciar servidor MCP con transporte SSE
    print(f"🚀 Iniciando servidor MCP con SSE...")
    print(f"   Transporte: Server-Sent Events (SSE)")
    print(f"   Puerto: {HTTP_PORT}")
    print(f"\n📚 Herramientas MCP disponibles (21+ tools):")
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
    print(f"\n   🏆 Challenges (NUEVO):")
    print(f"      - get_player_challenges")
    print(f"\n   🖼️  Imágenes (Data Dragon - SIN rate limits):")
    print(f"      - get_champion_splash_urls ⚡ OPTIMIZADO")
    print(f"      - get_champion_images")
    print(f"      - get_multiple_champion_images")
    print(f"      - get_champion_data_with_images")
    print(f"      - get_profile_icon_url")
    print(f"      - get_latest_version")
    print(f"\n   🎁 WRAPPED (Para tu web app):")
    print(f"      - get_player_wrapped ⭐ PRINCIPAL")
    print(f"      - get_player_profile_complete")
    print(f"      - get_detailed_match_analysis")
    print(f"\n✅ Servidor MCP SSE listo. Presiona Ctrl+C para detener.")
    print(f"\n💡 Para usar con un agente MCP, configura:")
    print(f'   "transport": "sse"')
    print(f'   "url": "http://localhost:{HTTP_PORT}/sse"')
    print(f"\n🎯 Para el Wrapped usa: get_player_wrapped(game_name, tag_line, region)")
    print(f"🖼️ Para imágenes usa: get_champion_splash_urls(champion_ids) ⚡ OPTIMIZADO\n")
    
    # Iniciar servidor MCP en modo SSE
    # FastMCP manejará el servidor HTTP internamente
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
