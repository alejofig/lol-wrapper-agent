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
} from '../lib/appsyncClient';
import ChampionsCarousel from './ChampionsCarousel';
import MasteriesCarousel from './MasteriesCarousel';

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
        <div className="section champions-section" style={{ padding: '3rem 2rem' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Tus campeones más jugados</h2>
          <ChampionsCarousel champions={stats.top_champions} />
        </div>
      )}

      {/* Top Maestrías - Carousel */}
      {parsedData.top_masteries && parsedData.top_masteries.length > 0 && (
        <div className="section masteries-section" style={{ padding: '3rem 2rem' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>⭐ Top Maestrías</h2>
          <MasteriesCarousel masteries={parsedData.top_masteries} />
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

      {/* Análisis Temporal Mejorado */}
      {(temporal.most_active_month || temporal.favorite_time_of_day || temporal.favorite_weekday) && (
        <div className="section temporal enhanced-temporal">
          <h2 className="temporal-title">
            <span role="img" aria-label="calendar">📅</span> ¿Cuándo juegas más?
          </h2>
          <div className="temporal-cards-row">
            {temporal.most_active_month && (
              <div className="temporal-card highlight-month">
                <div className="temporal-icon-bg month">
                  <span role="img" aria-label="month">📆</span>
                </div>
                <div>
                  <p className="temporal-label">Mes Más Activo</p>
                  <p className="temporal-value large">{temporal.most_active_month.month}</p>
                  <p className="temporal-secondary">{temporal.most_active_month.games.toLocaleString()} partida{temporal.most_active_month.games === 1 ? '' : 's'}</p>
                </div>
              </div>
            )}
            {temporal.favorite_time_of_day && (
              <div className="temporal-card highlight-time">
                <div className="temporal-icon-bg time">
                  {temporal.favorite_time_of_day === 'mañana' && <span role="img" aria-label="mañana">🌅</span>}
                  {temporal.favorite_time_of_day === 'tarde' && <span role="img" aria-label="tarde">☀️</span>}
                  {temporal.favorite_time_of_day === 'noche' && <span role="img" aria-label="noche">🌙</span>}
                  {temporal.favorite_time_of_day === 'madrugada' && <span role="img" aria-label="madrugada">🌃</span>}
                </div>
                <div>
                  <p className="temporal-label">Horario Favorito</p>
                  <p className="temporal-value large">
                    {temporal.favorite_time_of_day.charAt(0).toUpperCase() + temporal.favorite_time_of_day.slice(1)}
                  </p>
                </div>
              </div>
            )}
            {temporal.favorite_weekday && (
              <div className="temporal-card highlight-weekday">
                <div className="temporal-icon-bg weekday">
                  <span role="img" aria-label="weekday">🗓️</span>
                </div>
                <div>
                  <p className="temporal-label">Día Favorito</p>
                  <p className="temporal-value large">{temporal.favorite_weekday}</p>
                  <p className="temporal-secondary">{temporal.favorite_weekday_games.toLocaleString()} partida{temporal.favorite_weekday_games === 1 ? '' : 's'}</p>
                </div>
              </div>
            )}
          </div>
          <style>{`
             .enhanced-temporal {
               margin-top: 2.3rem;
               margin-bottom: 2.7rem;
               padding: 2.4rem 2rem 2.2rem 2rem;
               background: linear-gradient(145deg, rgba(1, 10, 19, 0.8), rgba(15, 35, 65, 0.6));
               border-radius: 16px;
               box-shadow: 
                 0 8px 32px rgba(0, 9, 19, 0.5),
                 0 0 40px rgba(200, 155, 60, 0.15),
                 inset 0 1px 0 rgba(200, 155, 60, 0.2);
               border: 2px solid rgba(200, 155, 60, 0.3);
             }
            .temporal-title {
              font-size: 1.5rem;
              font-weight: 800;
              color: #ffdcae;
              text-align: center;
              letter-spacing: 0.01em;
              margin-bottom: 1.7rem;
              text-shadow: 0 0 9px #f7e3b310;
            }
            .temporal-cards-row {
              display: flex;
              justify-content: center;
              gap: 2.3rem;
              flex-wrap: wrap;
            }
             .temporal-card {
               display: flex;
               align-items: center;
               gap: 1.2rem;
               background: linear-gradient(145deg, rgba(0, 9, 19, 0.7), rgba(15, 35, 65, 0.5));
               border-radius: 12px;
               min-width: 220px;
               padding: 1.25rem 2rem 1.1rem 1.35rem;
               box-shadow: 
                 0 4px 20px rgba(0, 9, 19, 0.4),
                 inset 0 1px 0 rgba(200, 155, 60, 0.1);
               border: 2px solid rgba(200, 155, 60, 0.2);
               transition: all 0.3s ease;
             }
            .temporal-card:hover {
              transform: translateY(-5px);
              border-color: rgba(200, 155, 60, 0.6);
              box-shadow: 
                0 8px 30px rgba(0, 9, 19, 0.6),
                0 0 25px rgba(200, 155, 60, 0.3),
                inset 0 1px 0 rgba(200, 155, 60, 0.3);
            }
            .temporal-icon-bg {
              background: linear-gradient(145deg, rgba(15, 35, 65, 0.8), rgba(200, 155, 60, 0.6));
              border-radius: 50%;
              width: 60px;
              height: 60px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 2.3em;
              box-shadow: 
                0 4px 15px rgba(0, 9, 19, 0.4),
                0 0 20px rgba(200, 155, 60, 0.2);
              margin-right: 0.2rem;
              border: 2px solid rgba(200, 155, 60, 0.3);
            }
            .temporal-label {
              font-size: 1.04rem;
              color: #f3cc73;
              text-shadow: 0 0 6px #c8aa6e1a;
              font-weight: 600;
              margin-bottom: 0.19em;
              letter-spacing: 0.04em;
              text-transform: uppercase;
            }
            .temporal-value {
              color: #ffdcae;
              font-weight: 900;
              font-size: 1.32rem;
              letter-spacing: 0.02em;
              margin-bottom: 0.18em;
              text-shadow: 0 0 9px #f7e3b38a;
            }
            .temporal-value.large {
              font-size: 1.55rem;
              letter-spacing: 0.033em;
              color: #fff3c3;
              text-shadow: 0 2px 16px #c8aa6e65;
            }
            .temporal-secondary {
              font-size: 1em;
              color: #9bb1cf;
              margin-top: 0.2em;
              letter-spacing: 0.01em;
            }
            @media (max-width: 750px) {
              .temporal-cards-row {
                flex-direction: column;
                gap: 1.3rem;
                align-items: stretch;
              }
              .enhanced-temporal {
                padding: 1.2rem;
              }
              .temporal-card {
                min-width: unset;
                width: 99%;
                padding: 1rem 1.3rem;
                margin: 0 auto;
              }
            }
          `}</style>
        </div>
      )}

      {/* Desafíos */}
      {challenges.total_points > 0 && (
        <div className="section challenges improved-challenges">
          <h2 className="challenges-title">
            <span role="img" aria-label="trophy" className="trophy-emoji">🏆</span> 
            Desafíos y Logros
          </h2>
          <div className="challenges-cards-row">
            <div className="challenge-card total-points">
              <div className="challenge-icon-bg">
                <span role="img" aria-label="gem">💎</span>
              </div>
              <div>
                <p className="challenge-label">Puntos Totales</p>
                <p className="challenge-value highlight">{challenges.total_points?.toLocaleString()}</p>
              </div>
            </div>
            <div className="challenge-card total-level">
              <div className="challenge-icon-bg">
                <span role="img" aria-label="medal">🎖️</span>
              </div>
              <div>
                <p className="challenge-label">Nivel Global</p>
                <p className="challenge-value highlight">{challenges.total_level}</p>
              </div>
            </div>
          </div>

          {challenges.percentile_achievements && challenges.percentile_achievements.length > 0 && (
            <div className="percentile-badges-grid">
              {(() => {
                const top1 = challenges.percentile_achievements.filter((p: any) => p.tier === 'top_1_percent').length;
                const top5 = challenges.percentile_achievements.filter((p: any) => p.tier === 'top_5_percent').length;
                const top10 = challenges.percentile_achievements.filter((p: any) => p.tier === 'top_10_percent').length;

                return (
                  <>
                    {top1 > 0 && (
                      <div className="badge enhanced top1">
                        <span className="badge-emoji" role="img" aria-label="star">⭐</span>
                        <span className="badge-label">TOP 1%</span>
                        <span className="badge-count">{top1} {top1 === 1 ? 'desafío' : 'desafíos'}</span>
                      </div>
                    )}
                    {top5 > 0 && (
                      <div className="badge enhanced top5">
                        <span className="badge-emoji" role="img" aria-label="sparkle">🌟</span>
                        <span className="badge-label">TOP 5%</span>
                        <span className="badge-count">{top5} {top5 === 1 ? 'desafío' : 'desafíos'}</span>
                      </div>
                    )}
                    {top10 > 0 && (
                      <div className="badge enhanced top10">
                        <span className="badge-emoji" role="img" aria-label="sparkles">✨</span>
                        <span className="badge-label">TOP 10%</span>
                        <span className="badge-count">{top10} {top10 === 1 ? 'desafío' : 'desafíos'}</span>
                      </div>
                    )}
                  </>
                );
              })()}
            </div>
          )}

          {/* Stilos para mejorar visualmente la sección de desafíos */}
          <style>{`
            .improved-challenges {
              background: linear-gradient(120deg, rgba(1,10,19,0.93), rgba(200,155,60,0.05) 130%);
              margin-block: 3rem 2rem;
              padding-top: 2.5rem;
              padding-bottom: 2.5rem;
              border-radius: 20px;
              box-shadow:
                0 8px 32px rgba(0,9,19,0.32),
                0 0 35px rgba(200,155,60,0.07),
                inset 0 1px 0 rgba(200,155,60,0.09);
            }
            .challenges-title {
              font-size: 2rem;
              margin-bottom: 2.1rem;
              font-weight: 800;
              color: #f3cc73;
              letter-spacing: 0.04em;
              text-shadow: 0 0 18px #c89b3c77, 0 2px 8px #00091680;
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 0.5em;
            }
            .trophy-emoji {
              font-size: 2.3rem;
              filter: drop-shadow(0 0 12px #c89b3c88);
            }
            .challenges-cards-row {
              display: flex;
              justify-content: center;
              gap: 2.5rem;
              margin-bottom: 2.2rem;
              flex-wrap: wrap;
            }
            .challenge-card {
              background: linear-gradient(120deg, rgba(200,155,60,0.12) 0%, rgba(1,10,19,0.25) 85%);
              border: 1.8px solid rgba(200,155,60,0.30);
              border-radius: 18px;
              padding: 1.6rem 2.1rem 1.1rem 2.1rem;
              box-shadow: 0 2px 12px rgba(200,155,60,0.08), 0 1px 6px rgba(15,35,65,0.09);
              display: flex;
              align-items: center;
              gap: 1.4rem;
              min-width: 190px;
            }
            .challenge-icon-bg {
              background: radial-gradient(circle, #c89b3cbb 0%, #1a273e 75%);
              border-radius: 50%;
              width: 55px;
              height: 55px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 2.1rem;
              box-shadow: 0 0 25px 4px #c89b3c25, 0 2px 18px #00091622;
              margin-right: 0.2rem;
            }
            .challenge-label {
              font-size: 1.06rem;
              color: #c8aa6e;
              text-shadow: 0 0 6px #c8aa6e1b;
              font-weight: 700;
              margin-bottom: 0.13em;
              letter-spacing: 0.04em;
            }
            .challenge-value {
              font-size: 1.6rem;
              color: #ffdcae;
              font-weight: 900;
              letter-spacing: 0.03em;
              margin: 0;
            }
            .challenge-value.highlight {
              color: #f8e9bd;
              text-shadow: 0 1px 15px #ceba7977, 0 0 22px #a28c470a;
            }
            .percentile-badges-grid {
              display: flex;
              justify-content: center;
              align-items: center;
              flex-wrap: wrap;
              gap: 1.2rem;
              margin: 1.3rem 0 0.25rem 0;
            }
            .badge.enhanced {
              display: flex;
              align-items: center;
              background: linear-gradient(135deg, rgba(200,155,60,0.13), rgba(15,35,65,0.16) 65%);
              border: 2px solid rgba(200,155,60,0.38);
              border-radius: 14px;
              box-shadow: 0 1px 8px 0px #eee1c326, 0 0 24px #c89b3c12;
              padding: 0.75em 1.5em;
              font-size: 1.06rem;
              gap: 0.85em;
              font-weight: 800;
              color: #cfb377;
              text-shadow: 0 0 7px #c89b3c44;
              letter-spacing: 0.02em;
              transition: transform 0.15s;
            }
            .badge.enhanced:hover {
              background: linear-gradient(135deg, rgba(200,155,60,0.25), rgba(15,35,65,0.22) 70%);
              border-color: #f7e8ae;
              color: #ffd464;
              transform: scale(1.04) rotate(-2deg);
              box-shadow: 0 4px 16px #f7e8ae54, 0 0 32px #f7e8ae33;
            }
            .badge-emoji {
              font-size: 1.35em;
              margin-right: 0.2em;
              filter: drop-shadow(0 0 6px #c89b3c50);
            }
            .badge-label {
              margin-right: 0.36em;
              font-size: 1em;
              text-transform: uppercase;
              color: #f3cc73;
              text-shadow: 0 0 9px #c89b3c44;
              font-weight: 900;
              letter-spacing: 0.03em;
            }
            .badge-count {
              font-size: 0.99em;
              color: #e6e2df;
              font-weight: 600;
            }
            @media (max-width: 650px) {
              .challenges-cards-row { flex-direction: column; gap: 1rem;}
              .challenge-card { min-width: unset; width: 100%; justify-content: flex-start;}
              .improved-challenges { padding: 1.2rem; }
              .percentile-badges-grid { flex-direction: column; gap: 0.65rem; }
            }
          `}</style>
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
    max-width: 650px;
    margin: 4rem auto;
    padding: 4rem;
    text-align: center;
    background: linear-gradient(145deg, rgba(1, 10, 19, 0.95), rgba(15, 35, 65, 0.85));
    border: 2px solid rgba(200, 155, 60, 0.4);
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.7),
      0 0 60px rgba(200, 155, 60, 0.2),
      inset 0 1px 0 rgba(200, 155, 60, 0.3);
    position: relative;
    overflow: hidden;
  }

  .state-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at center, rgba(200, 155, 60, 0.08) 0%, transparent 70%);
    pointer-events: none;
  }

  .state-container > * {
    position: relative;
    z-index: 1;
  }

  .icon {
    font-size: 5rem;
    margin-bottom: 1.5rem;
    filter: drop-shadow(0 0 20px rgba(200, 155, 60, 0.4));
  }

  .spinner {
    border: 4px solid rgba(200, 155, 60, 0.2);
    border-top: 4px solid #C89B3C;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1.5rem;
    filter: drop-shadow(0 0 10px rgba(200, 155, 60, 0.5));
  }

  .spinner.large {
    width: 90px;
    height: 90px;
    border-width: 6px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .btn-generate, .btn-retry, .btn-share {
    padding: 1.2rem 2.5rem;
    background: linear-gradient(145deg, rgba(200, 155, 60, 0.9), rgba(200, 155, 60, 0.7));
    color: #0F2341;
    border: 2px solid rgba(200, 155, 60, 0.6);
    border-radius: 12px;
    font-size: 1.2rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    cursor: pointer;
    margin-top: 1.5rem;
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    box-shadow: 
      0 4px 15px rgba(0, 9, 19, 0.4),
      0 0 20px rgba(200, 155, 60, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
  }

  .btn-generate::before, .btn-retry::before, .btn-share::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
  }

  .btn-generate:hover::before, .btn-retry:hover::before, .btn-share:hover::before {
    left: 100%;
  }

  .btn-generate:hover, .btn-retry:hover, .btn-share:hover {
    transform: translateY(-3px);
    background: linear-gradient(145deg, rgba(200, 155, 60, 1), rgba(200, 155, 60, 0.8));
    border-color: rgba(200, 155, 60, 1);
    box-shadow: 
      0 8px 25px rgba(0, 9, 19, 0.6),
      0 0 30px rgba(200, 155, 60, 0.5),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }

  .error-message {
    color: #ff6b6b;
    margin: 1.5rem 0;
    padding: 1.2rem 1.5rem;
    background: linear-gradient(145deg, rgba(255, 50, 50, 0.15), rgba(139, 0, 0, 0.1));
    border: 2px solid rgba(255, 100, 100, 0.3);
    border-radius: 8px;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  }

  .note {
    color: #A09B8C;
    font-size: 1rem;
    margin-top: 1.5rem;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 9, 19, 0.6);
  }

  .progress-info {
    margin-top: 2.5rem;
    text-align: left;
    background: rgba(15, 35, 65, 0.3);
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid rgba(200, 155, 60, 0.2);
  }

  .progress-info p {
    margin: 0.8rem 0;
    padding-left: 1.2rem;
    color: #F0E6D2;
    font-weight: 500;
  }

  /* Wrapped Display Styles */
  .wrapped-display {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    color: #F0E6D2;
    background: radial-gradient(ellipse at center, rgba(200, 155, 60, 0.03) 0%, rgba(15, 35, 65, 0.05) 50%, rgba(0, 9, 19, 0.1) 100%);
    min-height: 100vh;
  }

  .wrapped-header {
    text-align: center;
    margin-bottom: 4rem;
    padding: 3rem;
    background: linear-gradient(145deg, rgba(1, 10, 19, 0.9), rgba(15, 35, 65, 0.8));
    border: 2px solid rgba(200, 155, 60, 0.4);
    border-radius: 20px;
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.6),
      0 0 60px rgba(200, 155, 60, 0.2),
      inset 0 1px 0 rgba(200, 155, 60, 0.3);
    position: relative;
    overflow: hidden;
  }

  .wrapped-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at center, rgba(200, 155, 60, 0.1) 0%, transparent 70%);
    pointer-events: none;
  }

  .wrapped-header > * {
    position: relative;
    z-index: 1;
  }

  .wrapped-header h1 {
    font-size: 2.2rem;
    margin-bottom: 1.5rem;
    color: #C89B3C;
    text-transform: uppercase;
    font-weight: 900;
    letter-spacing: 0.05em;
    text-shadow: 
      0 0 20px rgba(200, 155, 60, 0.8),
      0 4px 8px rgba(0, 9, 19, 0.9);
  }

  .player-card {
    margin-top: 2rem;
  }

  .player-info h2 {
    font-size: 1.8rem;
    margin-bottom: 0.8rem;
    color: #C8AA6E;
    font-weight: 800;
    text-shadow: 
      0 0 15px rgba(200, 170, 110, 0.6),
      0 2px 4px rgba(0, 9, 19, 0.8);
  }

  .player-info p {
    color: #A09B8C;
    font-size: 1.2rem;
    font-weight: 600;
    text-shadow: 0 1px 3px rgba(0, 9, 19, 0.7);
  }

  .section {
    margin: 3rem 0;
    padding: 3rem;
    background: linear-gradient(145deg, rgba(1, 10, 19, 0.8), rgba(15, 35, 65, 0.6));
    border: 2px solid rgba(200, 155, 60, 0.3);
    border-radius: 16px;
    backdrop-filter: blur(15px);
    box-shadow: 
      0 8px 32px rgba(0, 9, 19, 0.5),
      0 0 40px rgba(200, 155, 60, 0.15),
      inset 0 1px 0 rgba(200, 155, 60, 0.2);
    position: relative;
    overflow: hidden;
  }

  .section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at center, rgba(200, 155, 60, 0.05) 0%, transparent 70%);
    pointer-events: none;
  }

  .section > * {
    position: relative;
    z-index: 1;
  }

  .section h2 {
    font-size: 1.6rem;
    margin-bottom: 2rem;
    color: #C89B3C;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-shadow: 
      0 0 15px rgba(200, 155, 60, 0.7),
      0 2px 4px rgba(0, 9, 19, 0.8);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 2rem;
    margin: 2.5rem 0;
  }

  .stat-card {
    background: linear-gradient(145deg, rgba(0, 9, 19, 0.7), rgba(15, 35, 65, 0.5));
    padding: 2.5rem;
    border-radius: 12px;
    text-align: center;
    border: 2px solid rgba(200, 155, 60, 0.2);
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    box-shadow: 
      0 4px 20px rgba(0, 9, 19, 0.4),
      inset 0 1px 0 rgba(200, 155, 60, 0.1);
  }

  .stat-card:hover {
    border-color: rgba(200, 155, 60, 0.6);
    transform: translateY(-8px);
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.6),
      0 0 30px rgba(200, 155, 60, 0.3),
      inset 0 1px 0 rgba(200, 155, 60, 0.3);
  }

  .stat-icon {
    font-size: 2.2rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 10px rgba(200, 155, 60, 0.4));
  }

  .stat-value {
    font-size: 2.2rem;
    font-weight: 900;
    color: #C89B3C;
    margin: 1rem 0;
    text-shadow: 
      0 0 10px rgba(200, 155, 60, 0.6),
      0 2px 4px rgba(0, 9, 19, 0.8);
  }

  .stat-detail {
    color: #A09B8C;
    font-size: 1rem;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0, 9, 19, 0.6);
  }

  .ranked-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
  }

  .ranked-card {
    background: linear-gradient(145deg, rgba(0, 9, 19, 0.6), rgba(15, 35, 65, 0.4));
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    border: 2px solid rgba(200, 155, 60, 0.3);
    box-shadow: 
      0 4px 20px rgba(0, 9, 19, 0.4),
      inset 0 1px 0 rgba(200, 155, 60, 0.2);
    transition: all 0.3s ease;
  }

  .ranked-card:hover {
    border-color: rgba(200, 155, 60, 0.6);
    transform: translateY(-5px);
    box-shadow: 
      0 8px 30px rgba(0, 9, 19, 0.6),
      0 0 25px rgba(200, 155, 60, 0.3),
      inset 0 1px 0 rgba(200, 155, 60, 0.3);
  }

  .ranked-card h3 {
    color: #C8AA6E;
    font-weight: 700;
    font-size: 1.3rem;
    margin-bottom: 1rem;
    text-shadow: 0 0 8px rgba(200, 170, 110, 0.5);
  }

  .ranked-card .rank {
    font-size: 1.8rem;
    font-weight: 900;
    color: #C89B3C;
    margin: 1rem 0;
    text-shadow: 
      0 0 15px rgba(200, 155, 60, 0.8),
      0 2px 4px rgba(0, 9, 19, 0.9);
  }

  .ranked-card p {
    color: #F0E6D2;
    font-weight: 600;
    margin: 0.5rem 0;
  }

  .ranked-card .record {
    color: #A09B8C;
    margin-top: 1rem;
    font-size: 1.1rem;
    font-weight: 500;
  }

  .champions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 2rem;
  }

  .champion-card {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    border: 2px solid rgba(200, 155, 60, 0.2);
    box-shadow: 0 4px 20px rgba(0, 9, 19, 0.4);
  }

  .champion-card:hover {
    transform: scale(1.08) translateY(-5px);
    border-color: rgba(200, 155, 60, 0.6);
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.6),
      0 0 30px rgba(200, 155, 60, 0.4);
  }

  .champion-splash {
    width: 100%;
    height: 280px;
    object-fit: cover;
    transition: all 0.3s ease;
  }

  .champion-card:hover .champion-splash {
    filter: brightness(1.1) contrast(1.1);
  }

  .champion-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0, 9, 19, 0.95), rgba(0, 9, 19, 0.3));
    padding: 1.5rem;
    color: #F0E6D2;
    border-top: 1px solid rgba(200, 155, 60, 0.3);
  }

  .champion-overlay h4 {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    color: #C8AA6E;
    text-shadow: 0 0 8px rgba(200, 170, 110, 0.6);
    text-transform: uppercase;
  }


  .game-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2.5rem;
  }

  .game-card {
    padding: 2.5rem;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 9, 19, 0.4);
    transition: all 0.3s ease;
  }

  .game-card:hover {
    transform: translateY(-5px);
  }

  .game-card.best {
    background: linear-gradient(145deg, rgba(76, 175, 80, 0.15), rgba(56, 142, 60, 0.1));
    border: 3px solid rgba(76, 175, 80, 0.6);
    box-shadow: 
      0 8px 32px rgba(0, 9, 19, 0.4),
      0 0 30px rgba(76, 175, 80, 0.2);
  }

  .game-card.best:hover {
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.6),
      0 0 40px rgba(76, 175, 80, 0.3);
  }

  .game-card.worst {
    background: linear-gradient(145deg, rgba(244, 67, 54, 0.15), rgba(198, 40, 40, 0.1));
    border: 3px solid rgba(244, 67, 54, 0.6);
    box-shadow: 
      0 8px 32px rgba(0, 9, 19, 0.4),
      0 0 30px rgba(244, 67, 54, 0.2);
  }

  .game-card.worst:hover {
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.6),
      0 0 40px rgba(244, 67, 54, 0.3);
  }

  .game-champion {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-radius: 8px;
    margin: 1.5rem 0;
    border: 2px solid rgba(200, 155, 60, 0.3);
    box-shadow: 0 4px 15px rgba(0, 9, 19, 0.4);
  }

  .champion-name {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 1rem 0;
    color: #C8AA6E;
    text-shadow: 0 0 8px rgba(200, 170, 110, 0.6);
    text-transform: uppercase;
  }

  .kda {
    font-size: 1.8rem;
    font-weight: 900;
    color: #C89B3C;
    text-shadow: 0 0 10px rgba(200, 155, 60, 0.6);
    margin: 0.5rem 0;
  }

  .kda-ratio, .result, .damage {
    margin: 0.5rem 0;
    color: #F0E6D2;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .result {
    font-size: 1.2rem;
    font-weight: 700;
    text-shadow: 0 1px 2px rgba(0, 9, 19, 0.6);
  }

  .multikill-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 2rem;
  }

  .multikill-card {
    padding: 3rem 2rem;
    border-radius: 16px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0, 9, 19, 0.4);
  }

  .multikill-card:hover {
    transform: translateY(-8px);
  }

  .multikill-card.penta {
    background: linear-gradient(145deg, rgba(255, 193, 7, 0.15), rgba(255, 152, 0, 0.1));
    border: 3px solid rgba(255, 193, 7, 0.8);
    box-shadow: 
      0 8px 32px rgba(0, 9, 19, 0.4),
      0 0 40px rgba(255, 193, 7, 0.3);
  }

  .multikill-card.penta:hover {
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.6),
      0 0 50px rgba(255, 193, 7, 0.4);
  }

  .multikill-card.quadra {
    background: linear-gradient(145deg, rgba(156, 39, 176, 0.15), rgba(123, 31, 162, 0.1));
    border: 3px solid rgba(156, 39, 176, 0.8);
    box-shadow: 
      0 8px 32px rgba(0, 9, 19, 0.4),
      0 0 40px rgba(156, 39, 176, 0.3);
  }

  .multikill-card.quadra:hover {
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.6),
      0 0 50px rgba(156, 39, 176, 0.4);
  }

  .multikill-card.triple {
    background: linear-gradient(145deg, rgba(33, 150, 243, 0.15), rgba(25, 118, 210, 0.1));
    border: 3px solid rgba(33, 150, 243, 0.8);
    box-shadow: 
      0 8px 32px rgba(0, 9, 19, 0.4),
      0 0 40px rgba(33, 150, 243, 0.3);
  }

  .multikill-card.triple:hover {
    box-shadow: 
      0 12px 40px rgba(0, 9, 19, 0.6),
      0 0 50px rgba(33, 150, 243, 0.4);
  }

  .multikill-icon {
    font-size: 2.8rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.3));
  }

  .multikill-count {
    font-size: 2.8rem;
    font-weight: 900;
    margin: 1rem 0;
    color: #F0E6D2;
    text-shadow: 
      0 0 15px rgba(255, 255, 255, 0.6),
      0 2px 4px rgba(0, 9, 19, 0.8);
  }

  .multikill-card h3 {
    color: #F0E6D2;
    font-weight: 700;
    font-size: 1.3rem;
    text-shadow: 0 1px 3px rgba(0, 9, 19, 0.7);
  }

  .temporal-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 2rem;
  }

  .temporal-card {
    padding: 2.5rem;
    background: linear-gradient(145deg, rgba(0, 9, 19, 0.6), rgba(15, 35, 65, 0.4));
    border: 2px solid rgba(200, 155, 60, 0.3);
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 9, 19, 0.4);
  }

  .temporal-card:hover {
    border-color: rgba(200, 155, 60, 0.6);
    transform: translateY(-5px);
    box-shadow: 
      0 8px 30px rgba(0, 9, 19, 0.6),
      0 0 25px rgba(200, 155, 60, 0.3);
  }

  .temporal-card h3 {
    font-size: 1.1rem;
    color: #A09B8C;
    margin-bottom: 1.5rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .temporal-value {
    font-size: 1.6rem;
    font-weight: 900;
    color: #C89B3C;
    margin: 1rem 0;
    text-shadow: 
      0 0 12px rgba(200, 155, 60, 0.7),
      0 2px 4px rgba(0, 9, 19, 0.8);
  }

  .temporal-card p {
    color: #F0E6D2;
    font-weight: 600;
    margin-top: 0.8rem;
  }

  .challenges-summary {
    display: flex;
    justify-content: space-around;
    margin: 3rem 0;
    gap: 2rem;
  }

  .challenge-stat {
    text-align: center;
    flex: 1;
  }

  .challenge-label {
    color: #A09B8C;
    margin-bottom: 1rem;
    font-size: 1.1rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .challenge-value {
    font-size: 1.8rem;
    font-weight: 900;
    color: #C89B3C;
    text-shadow: 
      0 0 15px rgba(200, 155, 60, 0.8),
      0 2px 4px rgba(0, 9, 19, 0.9);
  }

  .percentile-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    justify-content: center;
    margin-top: 3rem;
  }

  .badge {
    padding: 1rem 2rem;
    border-radius: 12px;
    font-weight: 800;
    text-align: center;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 9, 19, 0.3);
  }

  .badge:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 9, 19, 0.5);
  }

  .badge.top1 {
    background: linear-gradient(145deg, #ffd700, #ffed4e);
    color: #1a1a1a;
    border-color: #ffd700;
  }

  .badge.top1:hover {
    box-shadow: 0 8px 25px rgba(0, 9, 19, 0.5), 0 0 20px rgba(255, 215, 0, 0.4);
  }

  .badge.top5 {
    background: linear-gradient(145deg, #c0c0c0, #e0e0e0);
    color: #1a1a1a;
    border-color: #c0c0c0;
  }

  .badge.top5:hover {
    box-shadow: 0 8px 25px rgba(0, 9, 19, 0.5), 0 0 20px rgba(192, 192, 192, 0.4);
  }

  .badge.top10 {
    background: linear-gradient(145deg, #cd7f32, #e9a76a);
    color: #fff;
    border-color: #cd7f32;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  }

  .badge.top10:hover {
    box-shadow: 0 8px 25px rgba(0, 9, 19, 0.5), 0 0 20px rgba(205, 127, 50, 0.4);
  }

  .insights-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .insight-item {
    display: flex;
    align-items: flex-start;
    gap: 1.5rem;
    padding: 2rem;
    background: linear-gradient(145deg, rgba(0, 9, 19, 0.6), rgba(15, 35, 65, 0.4));
    border-radius: 12px;
    border-left: 4px solid #C89B3C;
    border: 2px solid rgba(200, 155, 60, 0.2);
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 9, 19, 0.3);
  }

  .insight-item:hover {
    border-color: rgba(200, 155, 60, 0.5);
    transform: translateY(-3px);
    box-shadow: 
      0 8px 30px rgba(0, 9, 19, 0.5),
      0 0 20px rgba(200, 155, 60, 0.2);
  }

  .insight-bullet {
    font-size: 2rem;
    flex-shrink: 0;
    filter: drop-shadow(0 0 8px rgba(200, 155, 60, 0.5));
  }

  .insight-item p {
    margin: 0;
    line-height: 1.7;
    color: #F0E6D2;
    font-size: 1.1rem;
    font-weight: 500;
  }

  .share-section {
    text-align: center;
    margin: 4rem 0;
    padding: 3rem;
    background: linear-gradient(145deg, rgba(1, 10, 19, 0.8), rgba(15, 35, 65, 0.6));
    border: 2px solid rgba(200, 155, 60, 0.3);
    border-radius: 16px;
    box-shadow: 
      0 8px 32px rgba(0, 9, 19, 0.5),
      0 0 40px rgba(200, 155, 60, 0.15);
  }

  .matches-info {
    color: #A09B8C;
    margin-top: 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0, 9, 19, 0.6);
  }

  @media (max-width: 768px) {
    .wrapped-display {
      padding: 1rem;
    }

    .wrapped-header {
      padding: 2rem 1.5rem;
      margin-bottom: 2rem;
    }

    .wrapped-header h1 {
      font-size: 2rem;
    }

    .player-info h2 {
      font-size: 1.8rem;
    }

    .section {
      padding: 2rem 1.5rem;
      margin: 2rem 0;
    }

    .section h2 {
      font-size: 1.8rem;
    }

    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
    }

    .stat-card {
      padding: 1.5rem;
    }

    .stat-value {
      font-size: 2rem;
    }

    .champions-grid {
      grid-template-columns: 1fr;
    }

    .ranked-grid {
      grid-template-columns: 1fr;
    }

    .temporal-grid {
      grid-template-columns: 1fr;
    }

    .multikill-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
    }

    .multikill-card {
      padding: 2rem 1rem;
    }

    .multikill-count {
      font-size: 2.5rem;
    }

    .game-cards {
      grid-template-columns: 1fr;
    }

    .challenges-summary {
      flex-direction: column;
      gap: 1.5rem;
    }

    .percentile-badges {
      gap: 1rem;
    }

    .badge {
      padding: 0.8rem 1.5rem;
      font-size: 1rem;
    }

    .insight-item {
      padding: 1.5rem;
      gap: 1rem;
    }

    .insight-bullet {
      font-size: 1.5rem;
    }

    .insight-item p {
      font-size: 1rem;
    }

    .share-section {
      padding: 2rem 1.5rem;
      margin: 2rem 0;
    }
  }
`;

// Inyectar estilos
if (typeof document !== 'undefined') {
  const styleEl = document.createElement('style');
  styleEl.textContent = styles;
  document.head.appendChild(styleEl);
}

