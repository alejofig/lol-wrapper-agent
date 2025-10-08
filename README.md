# 🎮 League of Legends Wrapped - MCP Server

Servidor MCP (Model Context Protocol) para crear un **"Wrapped del Año"** estilo Spotify de jugadores de League of Legends usando la API de Riot Games.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-0.2.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Características

- 🎁 **Wrapped Completo**: Genera estadísticas anuales detalladas de cualquier jugador
- 🔧 **20 Herramientas MCP**: Acceso completo a Champion Mastery, Ranked, Match History y más
- 🌍 **Todas las Regiones**: Soporta las 16 regiones de League of Legends
- ⚡ **FastMCP + SSE**: Servidor MCP optimizado para agentes de IA
- 📊 **Análisis Inteligente**: Procesa hasta 100 partidas con estadísticas agregadas
- 🎨 **Visualizador**: Convierte JSON en formato legible para humanos

## 📦 Instalación Rápida

```bash
# 1. Clonar o navegar al proyecto
cd /Users/alejandrofigueroa/Desktop/Alejofig/Proyectos/lol-wrapper

# 2. Instalar dependencias con uv
uv sync

# 3. Configurar API key de Riot Games
cp .env.example .env
# Editar .env y añadir tu RIOT_API_KEY

# 4. Iniciar servidor MCP
uv run python lol_wrapper/server_http.py
```

## 🚀 Uso Básico

### Con un Agente de IA (Pydantic AI, LangChain, etc.)

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

# Conectar al servidor MCP
mcp_server = MCPServerSSE(url="http://localhost:8000/sse/")

# Crear agente
agent = Agent(
    "openai:gpt-4o",
    system_prompt="Eres un experto en análisis de League of Legends",
    mcp_servers=[mcp_server]
)

# Generar Wrapped
async with agent.run_mcp_servers():
    result = await agent.run(
        "Genera el Wrapped 2024 del jugador Faker#KR1 en la región kr"
    )
    print(result.output)
```

### Ejecutar el Ejemplo Incluido

```bash
# Editar agent.py con el jugador que quieras
uv run python agent.py
```

Esto generará:
- 📄 `wrapped_output.json` - Datos completos en JSON
- 📺 Salida formateada en consola

## 🎯 Wrapped del Año - Herramienta Principal

La herramienta **`get_player_wrapped`** es todo lo que necesitas:

```python
# El agente solo necesita llamar:
get_player_wrapped(
    game_name="Faker",
    tag_line="KR1", 
    region="kr",
    match_count=100,  # Opcional, default: 100
    year=2024         # Opcional, default: año actual
)
```

### ✨ Retorna TODO esto en un JSON:

```json
{
  "player": {
    "game_name": "Faker",
    "tag_line": "KR1",
    "summoner_level": 589,
    "mastery_score": 1234
  },
  "ranked": [{
    "tier": "CHALLENGER",
    "rank": "I",
    "wins": 245,
    "losses": 123,
    "winrate": 66.5
  }],
  "top_masteries": [...],
  "statistics": {
    "total_games": 368,
    "wins": 245,
    "winrate": 66.5,
    "avg_kda": 4.8,
    "pentakills": 5,
    "top_champions": [...],
    "best_game": {...}
  },
  "insights": [
    "Jugaste 368 partidas este año",
    "¡Dominaste con 66.5% de victorias!",
    "..."
  ]
}
```

## 🛠️ Herramientas MCP Disponibles (20)

### 🎁 Wrapped / Analytics
- `get_player_wrapped` ⭐ - Wrapped completo del año
- `get_player_profile_complete` - Perfil + ranked + maestrías
- `get_detailed_match_analysis` - Análisis de partida específica

### 👤 Summoner & Account
- `get_summoner_by_name` - Buscar jugador por nombre
- `get_available_regions` - Listar regiones

### ⭐ Champion Mastery
- `get_champion_masteries` - Todas las maestrías
- `get_champion_mastery` - Maestría de campeón específico
- `get_top_champion_masteries` - Top N maestrías
- `get_mastery_score` - Puntuación total

### 🏆 Ranked / League
- `get_ranked_info` - Info de ranked
- `get_challenger_players` - Liga Challenger
- `get_grandmaster_players` - Liga Grandmaster
- `get_master_players` - Liga Master

### 📜 Match History
- `get_match_history` - Historial de partidas
- `get_match_details` - Detalles de partida
- `get_match_timeline` - Timeline minuto a minuto

### 🎮 Live Game
- `get_current_game` - Partida en curso
- `get_featured_games` - Partidas destacadas

### 🔄 Champion Rotation
- `get_free_champion_rotation` - Campeones gratis de la semana

## 🌍 Regiones Soportadas

| Región | Código | Región | Código |
|--------|--------|--------|--------|
| Latinoamérica Norte | `la1` | Brasil | `br1` |
| Latinoamérica Sur | `la2` | Norteamérica | `na1` |
| Europa Oeste | `euw1` | Europa NE | `eun1` |
| Korea | `kr` | Japón | `jp1` |
| Oceanía | `oc1` | Turquía | `tr1` |
| Rusia | `ru` | Filipinas | `ph2` |
| Singapur | `sg2` | Tailandia | `th2` |
| Taiwán | `tw2` | Vietnam | `vn2` |

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# API Key de Riot Games (obtener en https://developer.riotgames.com/)
RIOT_API_KEY=RGAPI-tu-key-aqui

# Región por defecto
DEFAULT_REGION=la1

# Tu OpenAI API Key (para el agente)
OPENAI_API_KEY=sk-...
```

### Rate Limits

**Development Key** (gratis):
- 20 requests / segundo
- 100 requests / 2 minutos
- ⚠️ Expira cada 24 horas

**Production Key** (requiere aplicación):
- 3,000 requests / 10 segundos
- 180,000 requests / 10 minutos

## 📊 Ejemplo: Wrapped en tu Web App

```python
from fastapi import FastAPI
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

app = FastAPI()

@app.post("/api/wrapped")
async def get_wrapped(game_name: str, tag_line: str, region: str = "la1"):
    """Endpoint para tu web app."""
    mcp_server = MCPServerSSE(url="http://localhost:8000/sse/")
    agent = Agent("openai:gpt-4o", mcp_servers=[mcp_server])
    
    async with agent.run_mcp_servers():
        result = await agent.run(
            f"Usa get_player_wrapped con game_name='{game_name}', "
            f"tag_line='{tag_line}', region='{region}', match_count=100"
        )
        return result.output
```

## 🔧 Troubleshooting

### Error 401 Unauthorized
**Causa**: API key inválida o expirada  
**Solución**: Regenera tu key en https://developer.riotgames.com/

### Error 429 Rate Limited
**Causa**: Excediste límite de requests  
**Solución**: Espera un momento. Development keys tienen límites bajos.

### Error 404 Not Found
**Causa**: Jugador no existe en esa región  
**Solución**: Verifica nombre, tag y región

### "Matches analyzed: 0"
**Causa**: Jugador sin partidas recientes en el año especificado  
**Solución**: Normal. El Wrapped mostrará perfil y maestrías

### Región incorrecta
**Causa**: El agente no está usando la región correcta  
**Solución**: Tag → Región (LAN → la1, NA1 → na1, etc.)

## 📁 Estructura del Proyecto

```
lol-wrapper/
├── lol_wrapper/
│   ├── __init__.py
│   ├── server_http.py      # Servidor MCP con SSE
│   ├── client.py            # Cliente de Riot API
│   ├── analytics.py         # Análisis y agregación
│   └── champions.py         # IDs y nombres de campeones
├── agent.py                 # Ejemplo de uso con agente
├── visualizer.py            # Visualizador de Wrapped
├── tests/                   # Tests unitarios
├── .env                     # Configuración (no incluido)
├── pyproject.toml          # Dependencias
└── README.md               # Este archivo
```

## 🧪 Testing

```bash
# Ejecutar tests
uv run pytest tests/ -v

# Probar servidor manualmente
uv run python lol_wrapper/server_http.py

# Probar con agente
uv run python agent.py
```

## 📚 Recursos

- [Documentación de Riot API](https://developer.riotgames.com/apis)
- [Champion Mastery v4](https://developer.riotgames.com/apis#champion-mastery-v4)
- [Match v5](https://developer.riotgames.com/apis#match-v5)
- [Discord de Riot Developers](https://discord.gg/riotgamesdevrel)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 TODO

- [ ] Cache de respuestas para optimizar rate limits
- [ ] Soporte para más APIs (TFT, Valorant)
- [ ] Docker support
- [ ] CI/CD con GitHub Actions
- [ ] Data Dragon integration para nombres de campeones
- [ ] Webhooks para actualizaciones en tiempo real
- [ ] Dashboard web para visualizar Wrapped

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles

