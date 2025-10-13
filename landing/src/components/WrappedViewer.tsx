/**
 * Componente principal para visualizar el Wrapped
 * Maneja los estados: not_found, processing, completed, failed
 */

import { useState, useEffect } from 'react';
import {
  getWrapped,
  requestWrapped,
  subscribeToWrappedStatus,
  pollWrappedStatus,
  type PlayerWrapped
} from '../lib/appsyncClient.ts';

interface WrappedViewerProps {
  gameName?: string;
  tagLine?: string;
  initialData?: PlayerWrapped | null;
}

export default function WrappedViewer({
  gameName: propGameName,
  tagLine: propTagLine,
  initialData
}: WrappedViewerProps) {
  // Obtener gameName y tagLine de props o de query params
  const getPlayerFromURL = () => {
    if (typeof window === 'undefined') return { gameName: '', tagLine: '' };
    
    const urlParams = new URLSearchParams(window.location.search);
    const playerParam = urlParams.get('player');
    
    if (playerParam) {
      const parts = playerParam.split('-');
      return {
        gameName: decodeURIComponent(parts[0] || ''),
        tagLine: decodeURIComponent(parts[1] || 'LAN')
      };
    }
    
    return { gameName: '', tagLine: '' };
  };

  const urlPlayer = getPlayerFromURL();
  const gameName = propGameName || urlPlayer.gameName;
  const tagLine = propTagLine || urlPlayer.tagLine;

  const [wrapped, setWrapped] = useState<PlayerWrapped | null>(initialData || null);
  const [loading, setLoading] = useState(!initialData);
  const [error, setError] = useState<string | null>(null);

  const playerId = `${gameName}#${tagLine}`;

  // Redirigir si no hay jugador
  useEffect(() => {
    if (!gameName || !tagLine) {
      window.location.href = '/';
    }
  }, []);

  useEffect(() => {
    if (!initialData) {
      loadWrapped();
    } else if (initialData.status === 'PROCESSING') {
      startPolling();
    }
  }, [gameName, tagLine]);

  async function loadWrapped() {
    try {
      setLoading(true);
      const result = await getWrapped(gameName, tagLine);
      setWrapped(result);

      if (result.status === 'PROCESSING') {
        startPolling();
      }
    } catch (err) {
      console.error('Error loading wrapped:', err);
      setError('Error al cargar el wrapped');
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateWrapped() {
    try {
      setLoading(true);
      setError(null);

      // Solicitar generación
      await requestWrapped(gameName, tagLine, 'la1');

      // Empezar a hacer polling
      startPolling();
    } catch (err: any) {
      console.error('Error requesting wrapped:', err);
      setError(err.message || 'Error al solicitar wrapped');
      setLoading(false);
    }
  }

  function startPolling() {
    // Usar polling para verificar el estado
    // En producción, las subscriptions serían mejores pero son más complejas
    pollWrappedStatus(gameName, tagLine, (data) => {
      setWrapped(data);

      if (data.status === 'COMPLETED') {
        setLoading(false);
      } else if (data.status === 'FAILED') {
        setError(data.error || 'Error al generar wrapped');
        setLoading(false);
      }
    }, 24, 10000); // 24 intentos x 10 segundos = 4 minutos max
  }

  // Estado: Loading inicial
  if (loading && !wrapped) {
    return <LoadingState message="Cargando..." />;
  }

  // Estado: NOT_FOUND - No existe wrapped
  if (wrapped?.status === 'NOT_FOUND' && !loading) {
    return (
      <NotFoundState
        gameName={gameName}
        tagLine={tagLine}
        onGenerate={handleGenerateWrapped}
        error={error}
      />
    );
  }

  // Estado: PROCESSING - Generando wrapped
  if (wrapped?.status === 'PROCESSING' || (loading && wrapped)) {
    return <ProcessingState gameName={gameName} tagLine={tagLine} />;
  }

  // Estado: FAILED - Error en generación
  if (wrapped?.status === 'FAILED' || error) {
    return (
      <ErrorState
        error={wrapped?.error || error || 'Error desconocido'}
        onRetry={handleGenerateWrapped}
      />
    );
  }

  // Debug logging
  console.log('🔍 Wrapped state:', wrapped);
  console.log('🔍 Wrapped status:', wrapped?.status);
  console.log('🔍 Has wrappedData:', !!wrapped?.wrappedData);
  console.log('🔍 wrappedData type:', typeof wrapped?.wrappedData);

  // Estado: COMPLETED - Mostrar wrapped
  if (wrapped?.status === 'COMPLETED' && wrapped.wrappedData) {
    console.log('✅ Wrapped COMPLETED, parsing data...');
    
    // Parse wrappedData si es string
    let parsedData = wrapped.wrappedData;
    if (typeof parsedData === 'string') {
      console.log('📝 wrappedData es string, parseando...');
      try {
        parsedData = JSON.parse(parsedData);
        console.log('✅ Datos parseados:', parsedData);
      } catch (e) {
        console.error('❌ Error parsing wrappedData:', e);
        return <ErrorState error="Error al parsear los datos del Wrapped" onRetry={handleGenerateWrapped} />;
      }
    } else {
      console.log('✅ wrappedData ya es objeto');
    }
    
    console.log('🎮 Mostrando WrappedDisplay con data:', parsedData);
    return <WrappedDisplay data={parsedData} />;
  }

  console.log('⏳ Mostrando LoadingState');
  return <LoadingState message="Cargando..." />;
}

// ===== SUB-COMPONENTES =====

function LoadingState({ message }: { message: string }) {
  return (
    <div className="state-container loading">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  );
}

function NotFoundState({
  gameName,
  tagLine,
  onGenerate,
  error
}: {
  gameName: string;
  tagLine: string;
  onGenerate: () => void;
  error: string | null;
}) {
  return (
    <div className="state-container not-found">
      <div className="icon">🎮</div>
      <h2>¡Hola {gameName}!</h2>
      <p>Aún no hemos generado tu Wrapped 2025</p>
      {error && <div className="error-message">{error}</div>}
      <button onClick={onGenerate} className="btn-generate">
        ✨ Generar mi Wrapped 2025
      </button>
      <p className="note">Esto tomará aproximadamente 60-90 segundos</p>
    </div>
  );
}

function ProcessingState({
  gameName,
  tagLine
}: {
  gameName: string;
  tagLine: string;
}) {
  return (
    <div className="state-container processing">
      <div className="spinner large"></div>
      <h2>Generando tu Wrapped... ⏳</h2>
      <p>Estamos analizando tus partidas del 2025</p>
      <p className="player-info">{gameName}#{tagLine}</p>
      <div className="progress-info">
        <p>⚡ Consultando API de Riot Games</p>
        <p>📊 Analizando estadísticas</p>
        <p>🎨 Preparando visualización</p>
        <p className="note">Esto puede tomar 60-90 segundos...</p>
      </div>
    </div>
  );
}

function ErrorState({
  error,
  onRetry
}: {
  error: string;
  onRetry: () => void;
}) {
  return (
    <div className="state-container error">
      <div className="icon">❌</div>
      <h2>Oops! Algo salió mal</h2>
      <p className="error-message">{error}</p>
      <button onClick={onRetry} className="btn-retry">
        🔄 Reintentar
      </button>
    </div>
  );
}

function WrappedDisplay({ data }: { data: any }) {
  console.log('🎨 WrappedDisplay - typeof data:', typeof data);
  
  // Si data es string, parsearlo aquí también
  let parsedData = data;
  if (typeof data === 'string') {
    console.log('⚠️ Data es STRING en WrappedDisplay, parseando...');
    try {
      parsedData = JSON.parse(data);
      console.log('✅ Data parseado exitosamente:', parsedData);
    } catch (e) {
      console.error('❌ Error parseando data:', e);
      return <div>Error: No se pudo parsear los datos</div>;
    }
  }
  
  const stats = parsedData.statistics || {};
  const player = parsedData.player || {};
  const challenges = parsedData.challenges || {};
  const temporal = stats.temporal_insights || {};
  const ranked = parsedData.ranked || [];
  
  console.log('🎨 Stats:', stats);
  console.log('🎨 Player:', player);
  
  return (
    <div className="wrapped-display">
      {/* Header con info del jugador */}
      <div className="wrapped-header">
        <h1>🎮 League of Legends Wrapped {parsedData.year || 2025}</h1>
        <div className="player-card">
          <div className="player-info">
            <h2>{player.game_name}#{player.tag_line}</h2>
            <p>Nivel {player.summoner_level} • Puntuación de Maestría: {player.mastery_score?.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Stats principales */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🎮</div>
          <h3>Partidas</h3>
          <p className="stat-value">{stats.total_games || 0}</p>
          <p className="stat-detail">{stats.wins || 0}W / {stats.losses || 0}L</p>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <h3>Winrate</h3>
          <p className="stat-value">{stats.winrate?.toFixed(1) || 0}%</p>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⚔️</div>
          <h3>KDA</h3>
          <p className="stat-value">{stats.avg_kda?.toFixed(2) || 0}</p>
          <p className="stat-detail">{stats.avg_kills?.toFixed(1)}/{stats.avg_deaths?.toFixed(1)}/{stats.avg_assists?.toFixed(1)}</p>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏱️</div>
          <h3>Tiempo Jugado</h3>
          <p className="stat-value">{(stats.total_playtime_minutes / 60)?.toFixed(1) || 0}h</p>
        </div>
      </div>

      {/* Ranked Info */}
      {ranked.length > 0 && (
        <div className="section">
          <h2>🏆 Ranked</h2>
          <div className="ranked-grid">
            {ranked.map((queue: any, i: number) => {
              const queueName = queue.queueType?.includes('SOLO') ? 'Solo/Duo' : 'Flex';
              const total = (queue.wins || 0) + (queue.losses || 0);
              const wr = total > 0 ? ((queue.wins / total) * 100).toFixed(1) : '0.0';
              
              return (
                <div key={i} className="ranked-card">
                  <h3>{queueName}</h3>
                  <p className="rank">{queue.tier} {queue.rank}</p>
                  <p>{queue.leaguePoints} LP</p>
                  <p className="record">{queue.wins}W / {queue.losses}L ({wr}%)</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Top Campeones */}
      {stats.top_champions && stats.top_champions.length > 0 && (
        <div className="section champions-section">
          <h2>🎯 Tus Campeones Más Jugados</h2>
          <div className="champions-grid">
            {stats.top_champions.slice(0, 5).map((champ: any, i: number) => (
              <div key={i} className="champion-card">
                {champ.splash && (
                  <img src={champ.splash} alt={champ.champion} className="champion-splash" />
                )}
                <div className="champion-overlay">
                  <h4>{champ.champion}</h4>
                  <p>{champ.games} partidas</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Maestrías */}
      {parsedData.top_masteries && parsedData.top_masteries.length > 0 && (
        <div className="section">
          <h2>⭐ Top Maestrías</h2>
          <div className="masteries-list">
            {parsedData.top_masteries.slice(0, 5).map((mastery: any, i: number) => (
              <div key={i} className="mastery-item">
                {mastery.splash && (
                  <img src={mastery.splash} alt="" className="mastery-icon" />
                )}
                <div className="mastery-info">
                  <h4>#{i + 1}</h4>
                  <p className="mastery-level">Nivel {mastery.championLevel}</p>
                  <p>{mastery.championPoints?.toLocaleString()} puntos</p>
                  {mastery.tokensEarned > 0 && <span className="token">🎖️ {mastery.tokensEarned}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Mejor/Peor Partida */}
      {stats.best_game && (
        <div className="section games-highlight">
          <h2>🌟 Highlights</h2>
          <div className="game-cards">
            <div className="game-card best">
              <h3>🌟 Mejor Partida</h3>
              {stats.best_game.splash && (
                <img src={stats.best_game.splash} alt={stats.best_game.champion} className="game-champion" />
              )}
              <p className="champion-name">{stats.best_game.champion}</p>
              <p className="kda">{stats.best_game.kills}/{stats.best_game.deaths}/{stats.best_game.assists}</p>
              <p className="kda-ratio">KDA: {stats.best_game.kda?.toFixed(2)}</p>
              <p className="result">{stats.best_game.win ? '✅ Victoria' : '❌ Derrota'}</p>
              <p className="damage">{stats.best_game.damage?.toLocaleString()} daño</p>
            </div>
            
            {stats.worst_game && (
              <div className="game-card worst">
                <h3>📉 Partida más Difícil</h3>
                {stats.worst_game.splash && (
                  <img src={stats.worst_game.splash} alt={stats.worst_game.champion} className="game-champion" />
                )}
                <p className="champion-name">{stats.worst_game.champion}</p>
                <p className="kda">{stats.worst_game.kills}/{stats.worst_game.deaths}/{stats.worst_game.assists}</p>
                <p className="kda-ratio">KDA: {stats.worst_game.kda?.toFixed(2)}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Multikills */}
      {(stats.pentakills > 0 || stats.quadrakills > 0 || stats.triplekills > 0) && (
        <div className="section multikills">
          <h2>🔥 Multikills</h2>
          <div className="multikill-grid">
            {stats.pentakills > 0 && (
              <div className="multikill-card penta">
                <span className="multikill-icon">💥</span>
                <h3>Pentakills</h3>
                <p className="multikill-count">{stats.pentakills}</p>
              </div>
            )}
            {stats.quadrakills > 0 && (
              <div className="multikill-card quadra">
                <span className="multikill-icon">💥</span>
                <h3>Quadrakills</h3>
                <p className="multikill-count">{stats.quadrakills}</p>
              </div>
            )}
            {stats.triplekills > 0 && (
              <div className="multikill-card triple">
                <span className="multikill-icon">💥</span>
                <h3>Triplekills</h3>
                <p className="multikill-count">{stats.triplekills}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Análisis Temporal */}
      {temporal.most_active_month && (
        <div className="section temporal">
          <h2>📅 Cuándo Juegas</h2>
          <div className="temporal-grid">
            {temporal.most_active_month && (
              <div className="temporal-card">
                <h3>📆 Mes Más Activo</h3>
                <p className="temporal-value">{temporal.most_active_month.month}</p>
                <p>{temporal.most_active_month.games} partidas</p>
              </div>
            )}
            {temporal.favorite_time_of_day && (
              <div className="temporal-card">
                <h3>🕐 Horario Favorito</h3>
                <p className="temporal-value">
                  {temporal.favorite_time_of_day === 'mañana' && '🌅 Mañana'}
                  {temporal.favorite_time_of_day === 'tarde' && '☀️ Tarde'}
                  {temporal.favorite_time_of_day === 'noche' && '🌙 Noche'}
                  {temporal.favorite_time_of_day === 'madrugada' && '🌃 Madrugada'}
                </p>
              </div>
            )}
            {temporal.favorite_weekday && (
              <div className="temporal-card">
                <h3>📅 Día Favorito</h3>
                <p className="temporal-value">{temporal.favorite_weekday}</p>
                <p>{temporal.favorite_weekday_games} partidas</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Desafíos */}
      {challenges.total_points > 0 && (
        <div className="section challenges">
          <h2>🏆 Desafíos y Logros</h2>
          <div className="challenges-summary">
            <div className="challenge-stat">
              <p className="challenge-label">Puntos Totales</p>
              <p className="challenge-value">{challenges.total_points?.toLocaleString()}</p>
            </div>
            <div className="challenge-stat">
              <p className="challenge-label">Nivel Global</p>
              <p className="challenge-value">{challenges.total_level}</p>
            </div>
          </div>
          
          {challenges.percentile_achievements && challenges.percentile_achievements.length > 0 && (
            <div className="percentile-badges">
              {(() => {
                const top1 = challenges.percentile_achievements.filter((p: any) => p.tier === 'top_1_percent').length;
                const top5 = challenges.percentile_achievements.filter((p: any) => p.tier === 'top_5_percent').length;
                const top10 = challenges.percentile_achievements.filter((p: any) => p.tier === 'top_10_percent').length;
                
                return (
                  <>
                    {top1 > 0 && <div className="badge top1">⭐ TOP 1%: {top1} desafíos</div>}
                    {top5 > 0 && <div className="badge top5">🌟 TOP 5%: {top5} desafíos</div>}
                    {top10 > 0 && <div className="badge top10">✨ TOP 10%: {top10} desafíos</div>}
                  </>
                );
              })()}
            </div>
          )}
        </div>
      )}

      {/* Insights */}
      {parsedData.insights && parsedData.insights.length > 0 && (
        <div className="section insights-section">
          <h2>💡 Tu Año en Resumen</h2>
          <div className="insights-list">
            {parsedData.insights.map((insight: string, i: number) => (
              <div key={i} className="insight-item">
                <span className="insight-bullet">✨</span>
                <p>{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Botón de compartir */}
      <div className="share-section">
        <button
          className="btn-share"
          onClick={() => {
            if (navigator.share) {
              navigator.share({
                title: `Mi Wrapped LoL 2025`,
                text: `¡Mira mi Wrapped de League of Legends 2025! ${stats.total_games} partidas, ${stats.winrate?.toFixed(1)}% WR`,
                url: window.location.href
              });
            } else {
              navigator.clipboard.writeText(window.location.href);
              alert('¡Link copiado al portapapeles!');
            }
          }}
        >
          📤 Compartir mi Wrapped
        </button>
        <p className="matches-info">Basado en {parsedData.matches_analyzed} partidas analizadas</p>
      </div>
    </div>
  );
}

// Estilos inline
const styles = `
  .state-container {
    max-width: 600px;
    margin: 4rem auto;
    padding: 3rem;
    text-align: center;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
    backdrop-filter: blur(10px);
  }

  .icon {
    font-size: 4rem;
    margin-bottom: 1rem;
  }

  .spinner {
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-top: 4px solid #5865f2;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }

  .spinner.large {
    width: 80px;
    height: 80px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .btn-generate, .btn-retry, .btn-share {
    padding: 1rem 2rem;
    background: linear-gradient(135deg, #5865f2, #4752c4);
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    margin-top: 1rem;
    transition: all 0.3s ease;
  }

  .btn-generate:hover, .btn-retry:hover, .btn-share:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(88, 101, 242, 0.3);
  }

  .error-message {
    color: #ff6b6b;
    margin: 1rem 0;
    padding: 1rem;
    background: rgba(255, 107, 107, 0.1);
    border-radius: 0.5rem;
  }

  .note {
    color: #999;
    font-size: 0.9rem;
    margin-top: 1rem;
  }

  .progress-info {
    margin-top: 2rem;
    text-align: left;
  }

  .progress-info p {
    margin: 0.5rem 0;
    padding-left: 1rem;
  }

  /* Wrapped Display Styles */
  .wrapped-display {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    color: #fff;
  }

  .wrapped-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(88, 101, 242, 0.2), rgba(71, 82, 196, 0.2));
    border-radius: 1rem;
  }

  .wrapped-header h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
  }

  .player-card {
    margin-top: 1rem;
  }

  .player-info h2 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  .player-info p {
    color: #aaa;
    font-size: 1.1rem;
  }

  .section {
    margin: 3rem 0;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
    backdrop-filter: blur(10px);
  }

  .section h2 {
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    color: #5865f2;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
  }

  .stat-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 2rem;
    border-radius: 1rem;
    text-align: center;
    border: 2px solid transparent;
    transition: all 0.3s ease;
  }

  .stat-card:hover {
    border-color: #5865f2;
    transform: translateY(-5px);
  }

  .stat-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
  }

  .stat-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #5865f2;
    margin: 0.5rem 0;
  }

  .stat-detail {
    color: #aaa;
    font-size: 0.9rem;
  }

  .ranked-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .ranked-card {
    background: rgba(255, 255, 255, 0.03);
    padding: 1.5rem;
    border-radius: 0.8rem;
    text-align: center;
  }

  .ranked-card .rank {
    font-size: 1.8rem;
    font-weight: bold;
    color: #ffb900;
    margin: 0.5rem 0;
  }

  .ranked-card .record {
    color: #aaa;
    margin-top: 0.5rem;
  }

  .champions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }

  .champion-card {
    position: relative;
    border-radius: 1rem;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s ease;
  }

  .champion-card:hover {
    transform: scale(1.05);
  }

  .champion-splash {
    width: 100%;
    height: 250px;
    object-fit: cover;
  }

  .champion-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
    padding: 1rem;
    color: white;
  }

  .champion-overlay h4 {
    margin: 0;
    font-size: 1.2rem;
  }

  .masteries-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .mastery-item {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    background: rgba(255, 255, 255, 0.03);
    padding: 1rem;
    border-radius: 0.8rem;
  }

  .mastery-icon {
    width: 80px;
    height: 80px;
    border-radius: 0.5rem;
    object-fit: cover;
  }

  .mastery-info h4 {
    color: #5865f2;
    font-size: 1.5rem;
    margin: 0;
  }

  .mastery-level {
    font-weight: bold;
    color: #ffb900;
    margin: 0.3rem 0;
  }

  .token {
    display: inline-block;
    margin-top: 0.5rem;
    padding: 0.3rem 0.6rem;
    background: rgba(255, 185, 0, 0.2);
    border-radius: 0.3rem;
    font-size: 0.9rem;
  }

  .game-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }

  .game-card {
    padding: 1.5rem;
    border-radius: 1rem;
    text-align: center;
  }

  .game-card.best {
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(56, 142, 60, 0.2));
    border: 2px solid #4caf50;
  }

  .game-card.worst {
    background: linear-gradient(135deg, rgba(244, 67, 54, 0.2), rgba(198, 40, 40, 0.2));
    border: 2px solid #f44336;
  }

  .game-champion {
    width: 100%;
    height: 150px;
    object-fit: cover;
    border-radius: 0.5rem;
    margin: 1rem 0;
  }

  .champion-name {
    font-size: 1.3rem;
    font-weight: bold;
    margin: 0.5rem 0;
  }

  .kda {
    font-size: 1.5rem;
    font-weight: bold;
    color: #5865f2;
  }

  .kda-ratio, .result, .damage {
    margin: 0.3rem 0;
    color: #aaa;
  }

  .multikill-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }

  .multikill-card {
    padding: 2rem;
    border-radius: 1rem;
    text-align: center;
  }

  .multikill-card.penta {
    background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 152, 0, 0.2));
    border: 2px solid #ffc107;
  }

  .multikill-card.quadra {
    background: linear-gradient(135deg, rgba(156, 39, 176, 0.2), rgba(123, 31, 162, 0.2));
    border: 2px solid #9c27b0;
  }

  .multikill-card.triple {
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.2), rgba(25, 118, 210, 0.2));
    border: 2px solid #2196f3;
  }

  .multikill-icon {
    font-size: 3rem;
  }

  .multikill-count {
    font-size: 3rem;
    font-weight: bold;
    margin: 0.5rem 0;
  }

  .temporal-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }

  .temporal-card {
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 0.8rem;
    text-align: center;
  }

  .temporal-card h3 {
    font-size: 1rem;
    color: #aaa;
    margin-bottom: 1rem;
  }

  .temporal-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: #5865f2;
    margin: 0.5rem 0;
  }

  .challenges-summary {
    display: flex;
    justify-content: space-around;
    margin: 2rem 0;
  }

  .challenge-stat {
    text-align: center;
  }

  .challenge-label {
    color: #aaa;
    margin-bottom: 0.5rem;
  }

  .challenge-value {
    font-size: 2rem;
    font-weight: bold;
    color: #ffb900;
  }

  .percentile-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
    margin-top: 2rem;
  }

  .badge {
    padding: 0.8rem 1.5rem;
    border-radius: 2rem;
    font-weight: bold;
    text-align: center;
  }

  .badge.top1 {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    color: #000;
  }

  .badge.top5 {
    background: linear-gradient(135deg, #c0c0c0, #e0e0e0);
    color: #000;
  }

  .badge.top10 {
    background: linear-gradient(135deg, #cd7f32, #e9a76a);
    color: #fff;
  }

  .insights-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .insight-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 0.5rem;
    border-left: 3px solid #5865f2;
  }

  .insight-bullet {
    font-size: 1.5rem;
    flex-shrink: 0;
  }

  .insight-item p {
    margin: 0;
    line-height: 1.6;
  }

  .share-section {
    text-align: center;
    margin: 3rem 0;
    padding: 2rem;
  }

  .matches-info {
    color: #aaa;
    margin-top: 1rem;
    font-size: 0.9rem;
  }

  @media (max-width: 768px) {
    .wrapped-display {
      padding: 1rem;
    }

    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
    }

    .champions-grid {
      grid-template-columns: 1fr;
    }

    .wrapped-header h1 {
      font-size: 1.8rem;
    }
  }
`;

// Inyectar estilos
if (typeof document !== 'undefined') {
  const styleEl = document.createElement('style');
  styleEl.textContent = styles;
  document.head.appendChild(styleEl);
}

