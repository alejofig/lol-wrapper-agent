/**
 * Componente de búsqueda de jugador
 * Permite al usuario ingresar su gameName y tagLine
 */

import { useState } from 'react';

interface PlayerSearchProps {
  onSearch?: (gameName: string, tagLine: string) => void;
}

export default function PlayerSearch({ onSearch }: PlayerSearchProps) {
  const [gameName, setGameName] = useState('');
  const [tagLine, setTagLine] = useState('LAN');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!gameName.trim()) {
      alert('Por favor ingresa tu nombre de invocador');
      return;
    }

    // Redirigir a la página del wrapped con query parameter
    const playerParam = `${encodeURIComponent(gameName)}-${encodeURIComponent(tagLine)}`;
    window.location.href = `/wrapped?player=${playerParam}`;
  };

  return (
    <div className="player-search">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="gameName">Nombre de Invocador</label>
          <input
            type="text"
            id="gameName"
            value={gameName}
            onChange={(e) => setGameName(e.target.value)}
            placeholder="Ej: Faker"
            className="input-field"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="tagLine">Región / Tag</label>
          <select
            id="tagLine"
            value={tagLine}
            onChange={(e) => setTagLine(e.target.value)}
            className="input-field"
          >
            <option value="LAN">LAN (Latinoamérica Norte)</option>
            <option value="LAS">LAS (Latinoamérica Sur)</option>
            <option value="NA1">NA1 (Norteamérica)</option>
            <option value="BR1">BR1 (Brasil)</option>
            <option value="EUW">EUW (Europa Oeste)</option>
            <option value="EUNE">EUNE (Europa Noreste)</option>
            <option value="KR">KR (Korea)</option>
            <option value="JP">JP (Japón)</option>
          </select>
        </div>

        <button type="submit" className="btn-primary">
          🎮 Ver mi Wrapped 2025
        </button>
      </form>

      <style>{`
        .player-search {
          max-width: 550px;
          margin: 2rem auto;
          padding: 3rem;
          background: linear-gradient(145deg, rgba(1, 10, 19, 0.95), rgba(15, 35, 65, 0.85));
          border: 2px solid rgba(200, 155, 60, 0.4);
          border-radius: 16px;
          backdrop-filter: blur(15px);
          box-shadow: 
            0 8px 32px rgba(0, 9, 19, 0.6),
            0 0 40px rgba(200, 155, 60, 0.2),
            inset 0 1px 0 rgba(200, 155, 60, 0.3);
          position: relative;
          overflow: hidden;
        }

        .player-search::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: radial-gradient(ellipse at center, rgba(200, 155, 60, 0.05) 0%, transparent 70%);
          pointer-events: none;
        }

        .search-form {
          display: flex;
          flex-direction: column;
          gap: 2rem;
          position: relative;
          z-index: 1;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.8rem;
        }

        .form-group label {
          font-weight: 700;
          color: #C8AA6E;
          font-size: 0.9rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          text-shadow: 0 0 5px rgba(200, 170, 110, 0.4);
        }

        .input-field {
          padding: 1rem 1.5rem;
          border: 2px solid rgba(200, 155, 60, 0.3);
          border-radius: 8px;
          background: linear-gradient(145deg, rgba(0, 9, 19, 0.8), rgba(15, 35, 65, 0.6));
          color: #F0E6D2;
          font-size: 1rem;
          font-weight: 500;
          transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
          box-shadow: inset 0 2px 4px rgba(0, 9, 19, 0.5);
        }

        .input-field:focus {
          outline: none;
          border-color: rgba(200, 155, 60, 0.8);
          background: linear-gradient(145deg, rgba(15, 35, 65, 0.9), rgba(200, 155, 60, 0.1));
          box-shadow: 
            inset 0 2px 4px rgba(0, 9, 19, 0.7),
            0 0 20px rgba(200, 155, 60, 0.3),
            0 4px 15px rgba(0, 9, 19, 0.4);
          color: #F0E6D2;
        }

        .input-field::placeholder {
          color: #A09B8C;
        }

        .btn-primary {
          padding: 1.2rem 2.5rem;
          background: linear-gradient(145deg, rgba(200, 155, 60, 0.9), rgba(200, 155, 60, 0.7));
          color: #0F2341;
          border: 2px solid rgba(200, 155, 60, 0.6);
          border-radius: 8px;
          font-size: 1.1rem;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
          box-shadow: 
            0 4px 15px rgba(0, 9, 19, 0.4),
            0 0 20px rgba(200, 155, 60, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
          position: relative;
          overflow: hidden;
        }

        .btn-primary::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
          transition: left 0.5s ease;
        }

        .btn-primary:hover::before {
          left: 100%;
        }

        .btn-primary:hover {
          transform: translateY(-3px);
          background: linear-gradient(145deg, rgba(200, 155, 60, 1), rgba(200, 155, 60, 0.8));
          border-color: rgba(200, 155, 60, 1);
          box-shadow: 
            0 8px 25px rgba(0, 9, 19, 0.6),
            0 0 30px rgba(200, 155, 60, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        .btn-primary:active {
          transform: translateY(-1px);
        }

        @media (max-width: 768px) {
          .player-search {
            max-width: 90%;
            padding: 2rem 1.5rem;
            margin: 1rem auto;
          }

          .form-group label {
            font-size: 0.9rem;
          }

          .input-field {
            padding: 0.9rem 1.2rem;
            font-size: 1rem;
          }

          .btn-primary {
            padding: 1rem 2rem;
            font-size: 1.1rem;
          }
        }
      `}</style>
    </div>
  );
}

