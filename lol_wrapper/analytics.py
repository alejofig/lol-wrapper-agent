"""Módulo de análisis y agregación de datos para Wrapped."""

from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta


def calculate_kda(kills: int, deaths: int, assists: int) -> float:
    """Calcula el KDA (Kill/Death/Assist ratio)."""
    if deaths == 0:
        return float(kills + assists)
    return round((kills + assists) / deaths, 2)


def analyze_match_history(matches: List[Dict[str, Any]], puuid: str) -> Dict[str, Any]:
    """
    Analiza el historial de partidas y genera estadísticas agregadas.
    
    Args:
        matches: Lista de partidas detalladas
        puuid: PUUID del jugador para identificarlo en las partidas
    
    Returns:
        Dict con estadísticas agregadas
    """
    stats = {
        "total_games": 0,
        "wins": 0,
        "losses": 0,
        "winrate": 0.0,
        "total_kills": 0,
        "total_deaths": 0,
        "total_assists": 0,
        "avg_kda": 0.0,
        "total_playtime_minutes": 0,
        "champions_played": Counter(),
        "roles_played": Counter(),
        "best_game": None,
        "worst_game": None,
        "pentakills": 0,
        "quadrakills": 0,
        "triplekills": 0,
        "first_bloods": 0,
        "champion_stats": defaultdict(lambda: {
            "games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0
        })
    }
    
    best_kda = -1
    worst_kda = float('inf')
    
    for match in matches:
        if not match or "info" not in match:
            continue
            
        info = match["info"]
        stats["total_games"] += 1
        
        # Encontrar al jugador en la partida
        player_data = None
        for participant in info.get("participants", []):
            if participant.get("puuid") == puuid:
                player_data = participant
                break
        
        if not player_data:
            continue
        
        # Estadísticas básicas
        won = player_data.get("win", False)
        kills = player_data.get("kills", 0)
        deaths = player_data.get("deaths", 0)
        assists = player_data.get("assists", 0)
        champion_name = player_data.get("championName", "Unknown")
        role = player_data.get("teamPosition", player_data.get("individualPosition", "UTILITY"))
        
        if won:
            stats["wins"] += 1
        else:
            stats["losses"] += 1
        
        stats["total_kills"] += kills
        stats["total_deaths"] += deaths
        stats["total_assists"] += assists
        stats["total_playtime_minutes"] += info.get("gameDuration", 0) // 60
        
        # Campeones y roles
        stats["champions_played"][champion_name] += 1
        stats["roles_played"][role] += 1
        
        # Stats por campeón
        champ_stat = stats["champion_stats"][champion_name]
        champ_stat["games"] += 1
        champ_stat["kills"] += kills
        champ_stat["deaths"] += deaths
        champ_stat["assists"] += assists
        if won:
            champ_stat["wins"] += 1
        
        # Multikills
        stats["pentakills"] += player_data.get("pentaKills", 0)
        stats["quadrakills"] += player_data.get("quadraKills", 0)
        stats["triplekills"] += player_data.get("tripleKills", 0)
        stats["first_bloods"] += 1 if player_data.get("firstBloodKill", False) else 0
        
        # Mejor/peor partida
        kda = calculate_kda(kills, deaths, assists)
        if kda > best_kda:
            best_kda = kda
            stats["best_game"] = {
                "match_id": match.get("metadata", {}).get("matchId"),
                "champion": champion_name,
                "kda": kda,
                "kills": kills,
                "deaths": deaths,
                "assists": assists,
                "win": won,
                "damage": player_data.get("totalDamageDealtToChampions", 0)
            }
        
        if kda < worst_kda:
            worst_kda = kda
            stats["worst_game"] = {
                "match_id": match.get("metadata", {}).get("matchId"),
                "champion": champion_name,
                "kda": kda,
                "kills": kills,
                "deaths": deaths,
                "assists": assists,
                "win": won
            }
    
    # Calcular promedios
    if stats["total_games"] > 0:
        stats["winrate"] = round((stats["wins"] / stats["total_games"]) * 100, 2)
        stats["avg_kda"] = calculate_kda(
            stats["total_kills"],
            stats["total_deaths"],
            stats["total_assists"]
        )
        stats["avg_kills"] = round(stats["total_kills"] / stats["total_games"], 2)
        stats["avg_deaths"] = round(stats["total_deaths"] / stats["total_games"], 2)
        stats["avg_assists"] = round(stats["total_assists"] / stats["total_games"], 2)
        stats["avg_game_duration"] = round(stats["total_playtime_minutes"] / stats["total_games"], 2)
    
    # Top campeones (convertir Counter a lista ordenada)
    stats["top_champions"] = [
        {"champion": champ, "games": count}
        for champ, count in stats["champions_played"].most_common(10)
    ]
    
    # Top roles
    stats["top_roles"] = [
        {"role": role, "games": count}
        for role, count in stats["roles_played"].most_common()
    ]
    
    # Stats detallados por campeón
    champion_details = []
    for champ, stat in stats["champion_stats"].items():
        if stat["games"] > 0:
            champion_details.append({
                "champion": champ,
                "games": stat["games"],
                "wins": stat["wins"],
                "winrate": round((stat["wins"] / stat["games"]) * 100, 2),
                "kda": calculate_kda(stat["kills"], stat["deaths"], stat["assists"]),
                "avg_kills": round(stat["kills"] / stat["games"], 2),
                "avg_deaths": round(stat["deaths"] / stat["games"], 2),
                "avg_assists": round(stat["assists"] / stat["games"], 2)
            })
    
    stats["champion_details"] = sorted(
        champion_details,
        key=lambda x: x["games"],
        reverse=True
    )[:10]
    
    # Limpiar contadores (no son serializables a JSON directamente)
    del stats["champions_played"]
    del stats["roles_played"]
    del stats["champion_stats"]
    
    return stats


def generate_wrapped_insights(stats: Dict[str, Any]) -> List[str]:
    """
    Genera insights interesantes para el Wrapped.
    
    Args:
        stats: Estadísticas agregadas del jugador
    
    Returns:
        Lista de insights/frases para mostrar
    """
    insights = []
    
    # Total de partidas
    if stats["total_games"] > 0:
        insights.append(f"Jugaste {stats['total_games']} partidas este año")
        
        # Tiempo jugado
        hours = stats["total_playtime_minutes"] / 60
        if hours >= 100:
            insights.append(f"Pasaste {int(hours)} horas en la Grieta del Invocador")
        
        # Winrate
        if stats["winrate"] >= 55:
            insights.append(f"¡Dominaste con {stats['winrate']}% de victorias!")
        elif stats["winrate"] >= 50:
            insights.append(f"Mantuviste un {stats['winrate']}% de winrate")
        else:
            insights.append(f"Winrate de {stats['winrate']}% - ¡el próximo año será mejor!")
        
        # Campeón principal
        if stats["top_champions"]:
            main_champ = stats["top_champions"][0]
            insights.append(f"Tu campeón principal fue {main_champ['champion']} con {main_champ['games']} partidas")
        
        # KDA
        if stats["avg_kda"] >= 3.0:
            insights.append(f"KDA impresionante de {stats['avg_kda']}")
        elif stats["avg_kda"] >= 2.0:
            insights.append(f"KDA sólido de {stats['avg_kda']}")
        
        # Multikills
        if stats["pentakills"] > 0:
            insights.append(f"¡Conseguiste {stats['pentakills']} Pentakill{'s' if stats['pentakills'] > 1 else ''}!")
        elif stats["quadrakills"] > 0:
            insights.append(f"Lograste {stats['quadrakills']} Quadrakill{'s' if stats['quadrakills'] > 1 else ''}")
        
        # First bloods
        if stats["first_bloods"] >= 10:
            insights.append(f"Dominaste el early game con {stats['first_bloods']} First Bloods")
        
        # Mejor partida
        if stats["best_game"]:
            best = stats["best_game"]
            insights.append(
                f"Tu mejor partida: {best['kills']}/{best['deaths']}/{best['assists']} "
                f"con {best['champion']} (KDA: {best['kda']})"
            )
    
    return insights


def filter_matches_by_year(match_ids: List[str], year: Optional[int] = None) -> List[str]:
    """
    Filtra IDs de partidas por año basándose en el timestamp en el ID.
    
    Args:
        match_ids: Lista de IDs de partidas
        year: Año a filtrar (None = año actual)
    
    Returns:
        Lista de IDs filtrados
    """
    if year is None:
        year = datetime.now().year
    
    # Los match IDs tienen formato: REGION_TIMESTAMP
    # El timestamp está en epoch time (seconds since 1970)
    start_of_year = datetime(year, 1, 1).timestamp() * 1000
    end_of_year = datetime(year + 1, 1, 1).timestamp() * 1000
    
    filtered = []
    for match_id in match_ids:
        try:
            # Extraer timestamp del match ID
            parts = match_id.split('_')
            if len(parts) >= 2:
                timestamp = int(parts[1])
                if start_of_year <= timestamp < end_of_year:
                    filtered.append(match_id)
        except (ValueError, IndexError):
            # Si no se puede parsear, incluir la partida
            filtered.append(match_id)
    
    return filtered

