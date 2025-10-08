"""Visualizador de Wrapped - Convierte JSON en formato legible."""
import json
from lol_wrapper.champions import get_champion_name

def visualize_wrapped(wrapped_json: str) -> str:
    """
    Convierte el JSON del Wrapped en un formato visual legible.
    
    Args:
        wrapped_json: JSON string del wrapped
        
    Returns:
        String formateado para mostrar
    """
    data = json.loads(wrapped_json) if isinstance(wrapped_json, str) else wrapped_json
    
    output = []
    output.append("=" * 80)
    output.append("🎮 LEAGUE OF LEGENDS WRAPPED 2024")
    output.append("=" * 80)
    
    # Jugador
    player = data.get("player", {})
    output.append(f"\n👤 JUGADOR: {player.get('game_name', 'Unknown')}#{player.get('tag_line', '')}")
    output.append(f"   Nivel: {player.get('summoner_level', 0)}")
    output.append(f"   Puntuación de Maestría Total: {player.get('mastery_score', 0)}")
    
    # Ranked
    ranked = data.get("ranked", [])
    if ranked:
        output.append(f"\n🏆 RANKED:")
        for queue in ranked:
            queue_name = "Solo/Duo" if "SOLO" in queue.get("queueType", "") else "Flex"
            tier = queue.get("tier", "UNRANKED")
            rank = queue.get("rank", "")
            lp = queue.get("leaguePoints", 0)
            wins = queue.get("wins", 0)
            losses = queue.get("losses", 0)
            total = wins + losses
            wr = (wins / total * 100) if total > 0 else 0
            
            output.append(f"\n   {queue_name}:")
            output.append(f"      Tier: {tier} {rank} - {lp} LP")
            output.append(f"      Record: {wins}W / {losses}L ({wr:.1f}% WR)")
    else:
        output.append(f"\n🏆 RANKED: Sin datos de ranked")
    
    # Top Maestrías
    masteries = data.get("top_masteries", [])
    if masteries:
        output.append(f"\n⭐ TOP {len(masteries)} CAMPEONES (Por Maestría):")
        for i, mastery in enumerate(masteries, 1):
            champ_id = mastery.get("championId", 0)
            champ_name = get_champion_name(champ_id)
            level = mastery.get("championLevel", 0)
            points = mastery.get("championPoints", 0)
            tokens = mastery.get("tokensEarned", 0)
            
            output.append(f"\n   {i}. {champ_name}")
            output.append(f"      Nivel: {level} | Puntos: {points:,} | Tokens: {tokens}")
    
    # Estadísticas de Partidas
    stats = data.get("statistics", {})
    total_games = stats.get("total_games", 0)
    
    if total_games > 0:
        output.append(f"\n📊 ESTADÍSTICAS DE PARTIDAS ({total_games} analizadas):")
        output.append(f"   Record: {stats.get('wins', 0)}W / {stats.get('losses', 0)}L ({stats.get('winrate', 0):.1f}% WR)")
        output.append(f"   KDA Promedio: {stats.get('avg_kda', 0):.2f}")
        output.append(f"   Kills/Deaths/Assists: {stats.get('avg_kills', 0):.1f} / {stats.get('avg_deaths', 0):.1f} / {stats.get('avg_assists', 0):.1f}")
        output.append(f"   Tiempo Jugado: {stats.get('total_playtime_minutes', 0) / 60:.1f} horas")
        
        # Multikills
        if stats.get('pentakills', 0) > 0 or stats.get('quadrakills', 0) > 0:
            output.append(f"\n🔥 MULTIKILLS:")
            if stats.get('pentakills', 0) > 0:
                output.append(f"   💥 Pentakills: {stats.get('pentakills', 0)}")
            if stats.get('quadrakills', 0) > 0:
                output.append(f"   💥 Quadrakills: {stats.get('quadrakills', 0)}")
            if stats.get('triplekills', 0) > 0:
                output.append(f"   💥 Triplekills: {stats.get('triplekills', 0)}")
        
        # Top campeones jugados
        top_champs = stats.get('top_champions', [])
        if top_champs:
            output.append(f"\n🎯 CAMPEONES MÁS JUGADOS:")
            for i, champ_data in enumerate(top_champs[:5], 1):
                champ_name = champ_data.get('champion', 'Unknown')
                games = champ_data.get('games', 0)
                output.append(f"   {i}. {champ_name} - {games} partidas")
        
        # Mejor partida
        best_game = stats.get('best_game')
        if best_game:
            output.append(f"\n🌟 MEJOR PARTIDA:")
            output.append(f"   {best_game.get('champion', 'Unknown')}: {best_game.get('kills', 0)}/{best_game.get('deaths', 0)}/{best_game.get('assists', 0)}")
            output.append(f"   KDA: {best_game.get('kda', 0):.2f} | {'Victoria' if best_game.get('win') else 'Derrota'}")
            output.append(f"   Daño: {best_game.get('damage', 0):,}")
    else:
        output.append(f"\n⚠️  SIN ESTADÍSTICAS DE PARTIDAS")
        output.append(f"   No se encontraron partidas recientes para analizar.")
        output.append(f"   Esto puede ser porque:")
        output.append(f"   - El jugador no tiene partidas en {data.get('year', 2024)}")
        output.append(f"   - El historial de partidas está vacío")
        output.append(f"   - Las partidas no están disponibles en la API")
    
    # Insights
    insights = data.get("insights", [])
    if insights:
        output.append(f"\n💡 INSIGHTS:")
        for insight in insights:
            output.append(f"   • {insight}")
    
    output.append(f"\n" + "=" * 80)
    output.append(f"Generado: {data.get('generated_at', 'N/A')}")
    output.append(f"Partidas analizadas: {data.get('matches_analyzed', 0)}")
    output.append("=" * 80)
    
    return "\n".join(output)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Leer de archivo
        with open(sys.argv[1], 'r') as f:
            wrapped_data = f.read()
    else:
        # Leer de stdin
        wrapped_data = sys.stdin.read()
    
    print(visualize_wrapped(wrapped_data))

