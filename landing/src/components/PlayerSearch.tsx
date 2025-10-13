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
          max-width: 500px;
          margin: 2rem auto;
          padding: 2rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 1rem;
          backdrop-filter: blur(10px);
        }

        .search-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group label {
          font-weight: 600;
          color: #f0f0f0;
          font-size: 0.9rem;
        }

        .input-field {
          padding: 0.75rem 1rem;
          border: 2px solid rgba(255, 255, 255, 0.1);
          border-radius: 0.5rem;
          background: rgba(0, 0, 0, 0.3);
          color: #fff;
          font-size: 1rem;
          transition: all 0.3s ease;
        }

        .input-field:focus {
          outline: none;
          border-color: #5865f2;
          background: rgba(0, 0, 0, 0.5);
        }

        .btn-primary {
          padding: 1rem 2rem;
          background: linear-gradient(135deg, #5865f2, #4752c4);
          color: white;
          border: none;
          border-radius: 0.5rem;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px rgba(88, 101, 242, 0.3);
        }

        .btn-primary:active {
          transform: translateY(0);
        }
      `}</style>
    </div>
  );
}

