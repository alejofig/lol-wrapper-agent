"""Módulo de análisis y agregación de datos para Wrapped."""

from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime


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
        year: Año a filtrar (None = 2025)
    
    Returns:
        Lista de IDs filtrados
    """
    if year is None:
        year = 2025  # Año por defecto para Wrapped
    
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


def analyze_challenges(challenges_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analiza los datos de desafíos de un jugador y extrae insights.
    
    Args:
        challenges_data: Datos de desafíos de la API
    
    Returns:
        Análisis estructurado de desafíos
    """
    if not challenges_data or "challenges" not in challenges_data:
        return {
            "total_points": 0,
            "top_challenges": [],
            "category_breakdown": {},
            "percentile_achievements": []
        }
    
    challenges = challenges_data.get("challenges", [])
    
    # Filtrar solo challenges con progreso
    active_challenges = [c for c in challenges if c.get("value", 0) > 0]
    
    # Ordenar por percentile (más alto = mejor)
    top_challenges = sorted(
        active_challenges,
        key=lambda x: x.get("percentile", 0),
        reverse=True
    )[:10]
    
    # Encontrar challenges en percentiles altos (top 10%, 5%, 1%)
    percentile_achievements = []
    for challenge in active_challenges:
        percentile = challenge.get("percentile", 0)
        level = challenge.get("level", "NONE")
        
        if percentile >= 0.99:
            percentile_achievements.append({
                "challenge_id": challenge.get("challengeId"),
                "level": level,
                "percentile": percentile,
                "value": challenge.get("value"),
                "tier": "top_1_percent"
            })
        elif percentile >= 0.95:
            percentile_achievements.append({
                "challenge_id": challenge.get("challengeId"),
                "level": level,
                "percentile": percentile,
                "value": challenge.get("value"),
                "tier": "top_5_percent"
            })
        elif percentile >= 0.90:
            percentile_achievements.append({
                "challenge_id": challenge.get("challengeId"),
                "level": level,
                "percentile": percentile,
                "value": challenge.get("value"),
                "tier": "top_10_percent"
            })
    
    # Análisis por categoría
    category_points = challenges_data.get("categoryPoints", {})
    category_breakdown = {}
    for category, data in category_points.items():
        category_breakdown[category] = {
            "current": data.get("current", 0),
            "level": data.get("level", "NONE"),
            "max": data.get("max", 0),
            "percentile": data.get("percentile", 0)
        }
    
    # Contar challenges por nivel
    level_counts = {}
    for challenge in active_challenges:
        level = challenge.get("level", "NONE")
        level_counts[level] = level_counts.get(level, 0) + 1
    
    return {
        "total_points": challenges_data.get("totalPoints", {}).get("current", 0),
        "total_level": challenges_data.get("totalPoints", {}).get("level", "NONE"),
        "top_challenges": [
            {
                "challenge_id": c.get("challengeId"),
                "level": c.get("level"),
                "percentile": c.get("percentile"),
                "value": c.get("value")
            }
            for c in top_challenges[:5]
        ],
        "category_breakdown": category_breakdown,
        "percentile_achievements": sorted(
            percentile_achievements,
            key=lambda x: x["percentile"],
            reverse=True
        ),
        "level_counts": level_counts,
        "total_active_challenges": len(active_challenges)
    }


def generate_challenge_insights(challenge_analysis: Dict[str, Any]) -> List[str]:
    """
    Genera insights motivacionales basados en los desafíos del jugador.
    
    Args:
        challenge_analysis: Análisis de desafíos procesado
    
    Returns:
        Lista de frases de insights
    """
    insights = []
    
    # Total points
    total_points = challenge_analysis.get("total_points", 0)
    if total_points > 0:
        insights.append(f"🏆 Acumulaste {total_points:,} puntos de desafíos!")
    
    # Nivel total
    total_level = challenge_analysis.get("total_level", "NONE")
    if total_level != "NONE":
        level_names = {
            "IRON": "Hierro",
            "BRONZE": "Bronce",
            "SILVER": "Plata",
            "GOLD": "Oro",
            "PLATINUM": "Platino",
            "DIAMOND": "Diamante",
            "MASTER": "Maestro",
            "GRANDMASTER": "Gran Maestro",
            "CHALLENGER": "Retador"
        }
        insights.append(f"🎖️ Tu nivel global de desafíos es: {level_names.get(total_level, total_level)}")
    
    # Percentile achievements
    percentile_achievements = challenge_analysis.get("percentile_achievements", [])
    top_1_percent = [p for p in percentile_achievements if p["tier"] == "top_1_percent"]
    top_5_percent = [p for p in percentile_achievements if p["tier"] == "top_5_percent"]
    top_10_percent = [p for p in percentile_achievements if p["tier"] == "top_10_percent"]
    
    if top_1_percent:
        insights.append(f"⭐ ¡INCREÍBLE! Estás en el TOP 1% en {len(top_1_percent)} desafío(s)")
    if top_5_percent:
        insights.append(f"🌟 Estás en el TOP 5% en {len(top_5_percent)} desafío(s)")
    if top_10_percent:
        insights.append(f"✨ Estás en el TOP 10% en {len(top_10_percent)} desafío(s)")
    
    # Nivel counts
    level_counts = challenge_analysis.get("level_counts", {})
    if "MASTER" in level_counts or "GRANDMASTER" in level_counts or "CHALLENGER" in level_counts:
        high_tier = sum([
            level_counts.get("MASTER", 0),
            level_counts.get("GRANDMASTER", 0),
            level_counts.get("CHALLENGER", 0)
        ])
        insights.append(f"👑 Alcanzaste nivel Maestro o superior en {high_tier} desafío(s)")
    
    # Categorías destacadas
    category_breakdown = challenge_analysis.get("category_breakdown", {})
    best_category = None
    best_percentile = 0
    
    category_names = {
        "VETERANCY": "Veteranía",
        "COLLECTION": "Colección",
        "EXPERTISE": "Experticia",
        "TEAMWORK": "Trabajo en Equipo",
        "IMAGINATION": "Imaginación"
    }
    
    for category, data in category_breakdown.items():
        percentile = data.get("percentile", 0)
        if percentile > best_percentile:
            best_percentile = percentile
            best_category = category
    
    if best_category and best_percentile >= 0.75:
        category_name = category_names.get(best_category, best_category)
        insights.append(f"🎯 Tu categoría más fuerte es {category_name} (Top {int((1-best_percentile)*100)}%)")
    
    # Total active challenges
    total_active = challenge_analysis.get("total_active_challenges", 0)
    if total_active > 50:
        insights.append(f"🔥 Tienes progreso en {total_active} desafíos diferentes")
    
    return insights

