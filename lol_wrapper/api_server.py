#!/usr/bin/env python3
"""Servidor REST API para agentes - League of Legends Champion Mastery.

Este servidor expone las herramientas como una API REST tradicional,
ideal para uso con agentes que consumen APIs HTTP.
"""

import os
import sys
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Asegurar que el directorio padre está en el path
if __name__ == "__main__":
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))

try:
    from .client import RiotAPIClient
except ImportError:
    from lol_wrapper.client import RiotAPIClient

# Cargar variables de entorno
load_dotenv()

# Configuración
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "na1")
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))

if not RIOT_API_KEY:
    raise ValueError("RIOT_API_KEY no encontrada en variables de entorno")

# Inicializar FastAPI
app = FastAPI(
    title="League of Legends Champion Mastery API",
    description="API REST para consultar maestrías de campeones de LoL",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir requests desde agentes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente global
client = RiotAPIClient(RIOT_API_KEY, DEFAULT_REGION)


# Modelos Pydantic para las requests
class SummonerRequest(BaseModel):
    game_name: str
    tag_line: str
    region: Optional[str] = None


class MasteryRequest(BaseModel):
    puuid: str
    region: Optional[str] = None


class ChampionMasteryRequest(BaseModel):
    puuid: str
    champion_id: int
    region: Optional[str] = None


class TopMasteriesRequest(BaseModel):
    puuid: str
    count: int = 3
    region: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    """Información del API."""
    return {
        "name": "League of Legends Champion Mastery API",
        "version": "0.1.0",
        "documentation": "/docs",
        "endpoints": {
            "summoner": "/summoner",
            "masteries": "/masteries",
            "mastery": "/mastery/{puuid}/{champion_id}",
            "top_masteries": "/top-masteries",
            "mastery_score": "/mastery-score/{puuid}",
            "regions": "/regions"
        }
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


@app.post("/summoner")
async def get_summoner(request: SummonerRequest):
    """
    Busca un invocador por nombre y tag.
    
    Returns información del jugador incluyendo PUUID.
    """
    try:
        result = await client.get_summoner_by_name(
            request.game_name,
            request.tag_line,
            request.region
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/masteries")
async def get_masteries(request: MasteryRequest):
    """
    Obtiene todas las maestrías de campeones de un jugador.
    """
    try:
        result = await client.get_champion_masteries(
            request.puuid,
            request.region
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/mastery/{puuid}/{champion_id}")
async def get_mastery(puuid: str, champion_id: int, region: Optional[str] = None):
    """
    Obtiene la maestría de un campeón específico.
    """
    try:
        result = await client.get_champion_mastery(
            puuid,
            champion_id,
            region
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/top-masteries")
async def get_top_masteries(request: TopMasteriesRequest):
    """
    Obtiene las top N maestrías de un jugador.
    """
    try:
        if request.count < 1 or request.count > 10:
            raise HTTPException(
                status_code=400,
                detail="count debe estar entre 1 y 10"
            )
        
        result = await client.get_top_champion_masteries(
            request.puuid,
            request.count,
            request.region
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/mastery-score/{puuid}")
async def get_mastery_score(puuid: str, region: Optional[str] = None):
    """
    Obtiene la puntuación total de maestría de un jugador.
    """
    try:
        result = await client.get_mastery_score(puuid, region)
        return {"puuid": puuid, "totalMasteryScore": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/regions")
async def get_regions():
    """
    Lista todas las regiones disponibles.
    """
    clusters = {
        "americas": ["br1", "la1", "la2", "na1", "oc1"],
        "asia": ["kr", "jp1"],
        "europe": ["eun1", "euw1", "tr1", "ru"],
        "sea": ["ph2", "sg2", "th2", "tw2", "vn2"]
    }
    
    return {
        "platforms": list(RiotAPIClient.PLATFORMS.keys()),
        "clusters": clusters,
        "default_region": DEFAULT_REGION
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar el servidor."""
    await client.close()


def main():
    """Punto de entrada principal."""
    print("🚀 Iniciando API REST para Agentes...")
    print(f"   Host: {HTTP_HOST}")
    print(f"   Puerto: {HTTP_PORT}")
    print(f"   URL: http://{HTTP_HOST}:{HTTP_PORT}")
    print(f"   Docs: http://{HTTP_HOST}:{HTTP_PORT}/docs")
    print(f"\n📚 Endpoints disponibles:")
    print(f"   POST /summoner - Buscar jugador")
    print(f"   POST /masteries - Obtener todas las maestrías")
    print(f"   GET  /mastery/{{puuid}}/{{champion_id}} - Maestría específica")
    print(f"   POST /top-masteries - Top N maestrías")
    print(f"   GET  /mastery-score/{{puuid}} - Puntuación total")
    print(f"   GET  /regions - Regiones disponibles")
    print(f"\n✅ Servidor listo. Presiona Ctrl+C para detener.\n")
    
    uvicorn.run(
        app,
        host=HTTP_HOST,
        port=HTTP_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()

