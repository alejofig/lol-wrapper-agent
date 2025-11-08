"""Cliente para interactuar con la API de Riot Games."""

import httpx
import asyncio
from typing import Optional, List, Dict, Any
from time import time
import os
import boto3
import json

from dotenv import load_dotenv
load_dotenv()

S3_BUCKET = os.getenv("S3_RAW_DATA_BUCKET")
s3_client = boto3.client("s3") 

class RiotAPIClient:
    """Cliente para la API de Riot Games."""
    
    # Mapeo de regiones a plataformas
    PLATFORMS = {
        "br1": "br1.api.riotgames.com",
        "eun1": "eun1.api.riotgames.com",
        "euw1": "euw1.api.riotgames.com",
        "jp1": "jp1.api.riotgames.com",
        "kr": "kr.api.riotgames.com",
        "la1": "la1.api.riotgames.com",
        "la2": "la2.api.riotgames.com",
        "na1": "na1.api.riotgames.com",
        "oc1": "oc1.api.riotgames.com",
        "ph2": "ph2.api.riotgames.com",
        "ru": "ru.api.riotgames.com",
        "sg2": "sg2.api.riotgames.com",
        "th2": "th2.api.riotgames.com",
        "tr1": "tr1.api.riotgames.com",
        "tw2": "tw2.api.riotgames.com",
        "vn2": "vn2.api.riotgames.com",
    }
    
    # Mapeo de regiones a clusters regionales (para Account API)
    REGIONAL_CLUSTERS = {
        "americas": "americas.api.riotgames.com",
        "asia": "asia.api.riotgames.com",
        "europe": "europe.api.riotgames.com",
        "sea": "sea.api.riotgames.com",
    }
    
    # Mapeo de plataformas a clusters regionales
    PLATFORM_TO_CLUSTER = {
        "br1": "americas",
        "la1": "americas",
        "la2": "americas",
        "na1": "americas",
        "oc1": "americas",
        "kr": "asia",
        "jp1": "asia",
        "eun1": "europe",
        "euw1": "europe",
        "tr1": "europe",
        "ru": "europe",
        "ph2": "sea",
        "sg2": "sea",
        "th2": "sea",
        "tw2": "sea",
        "vn2": "sea",
    }
    
    def __init__(self, api_key: str, default_region: str = "na1"):
        """
        Inicializa el cliente de la API de Riot Games.
        
        Args:
            api_key: Tu API key de Riot Games
            default_region: Región por defecto para las peticiones
        """
        self.api_key = api_key
        self.default_region = default_region
        self.client = httpx.AsyncClient(
            headers={"X-Riot-Token": api_key},
            timeout=30.0
        )
        
        # Rate limiting (Development Key limits)
        self._request_times = []  # Track request timestamps
        self._requests_per_second = 19  # Slightly under 20 to be safe
        self._requests_per_2min = 95  # Slightly under 100 to be safe
        self._rate_limit_lock = asyncio.Lock()
    
    async def _save_to_s3(self, url: str, data: Dict[str, Any], context_identifier: Optional[str] = None):
        """Guarda la respuesta de la API en S3 si el bucket está configurado."""
        if not S3_BUCKET or not data:
            return

        try:
            # El context_identifier (ej: NamiNami-LAN) es la única fuente de verdad para el nombre de la carpeta.
            player_folder = context_identifier.replace("#", "-") if context_identifier else "_global"
            path = url.split("api.riotgames.com")[1].split("?")[0]

            # Lógica para crear un nombre de archivo limpio y estructurado
            filename = ""
            if "/riot/account/v1/accounts/by-riot-id" in path:
                filename = "account-info.json"
            elif "/lol/summoner/v4/summoners/by-puuid" in path:
                filename = "summoner-info.json"
            elif "/lol/champion-mastery/v4/champion-masteries/by-puuid" in path:
                if "/top" in path:
                    filename = "mastery-top.json"
                else:
                    filename = "mastery-all.json"
            elif "/lol/champion-mastery/v4/scores/by-puuid" in path:
                filename = "mastery-score.json"
            elif "/lol/league/v4/entries/by-puuid" in path:
                filename = "league-entries.json"
            elif "/lol/match/v5/matches/by-puuid" in path:
                filename = "match-history.json"
            elif "/lol/match/v5/matches/" in path and "/timeline" not in path:
                match_id = path.split("/")[-1]
                filename = f"matches/{match_id}.json"
            elif "/lol/match/v5/matches/" in path and "/timeline" in path:
                match_id = path.split("/")[-2]
                filename = f"matches-timeline/{match_id}.json"
            elif "/lol/challenges/v1/player-data" in path:
                filename = "challenges-data.json"
            
            if not filename:
                return

            key = f"riot_api_responses/{player_folder}/{filename}"
            
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=json.dumps(data, indent=2),
                ContentType="application/json"
            )
        except Exception as e:
            print(f"Error al guardar en S3 ({url}): {e}")
    
    async def close(self):
        """Cierra el cliente HTTP."""
        await self.client.aclose()
    
    def _get_platform_url(self, region: str) -> str:
        """Obtiene la URL base para una región específica."""
        platform = self.PLATFORMS.get(region.lower())
        if not platform:
            raise ValueError(
                f"Región inválida: {region}. "
                f"Regiones válidas: {', '.join(self.PLATFORMS.keys())}"
            )
        return f"https://{platform}"
    
    def _get_regional_url(self, cluster: str) -> str:
        """Obtiene la URL base para un cluster regional."""
        regional_platform = self.REGIONAL_CLUSTERS.get(cluster.lower())
        if not regional_platform:
            raise ValueError(
                f"Cluster regional inválido: {cluster}. "
                f"Clusters válidos: {', '.join(self.REGIONAL_CLUSTERS.keys())}"
            )
        return f"https://{regional_platform}"
    
    async def _wait_for_rate_limit(self):
        """
        Espera si es necesario para respetar los rate limits.
        Development Key:
        - 20 requests/segundo
        - 100 requests/2 minutos
        """
        async with self._rate_limit_lock:
            now = time()
            
            # Limpiar requests antiguos (más de 2 minutos)
            self._request_times = [t for t in self._request_times if now - t < 120]
            
            # Verificar límite de 2 minutos
            if len(self._request_times) >= self._requests_per_2min:
                # Esperar hasta que el request más antiguo tenga 2 minutos
                oldest = self._request_times[0]
                wait_time = 120 - (now - oldest)
                if wait_time > 0:
                    await asyncio.sleep(wait_time + 0.1)
                    now = time()
                    self._request_times = [t for t in self._request_times if now - t < 120]
            
            # Verificar límite de 1 segundo
            recent = [t for t in self._request_times if now - t < 1.0]
            if len(recent) >= self._requests_per_second:
                # Esperar hasta el próximo segundo
                await asyncio.sleep(1.0 - (now - recent[0]) + 0.05)
            
            # Registrar esta petición
            self._request_times.append(time())
    
    async def _make_request(self, url: str, context_identifier: Optional[str] = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        Realiza una petición a la API con rate limiting y retry logic.
        
        Args:
            url: URL completa del endpoint
            max_retries: Número máximo de reintentos en caso de 429
            
        Returns:
            Respuesta JSON de la API
            
        Raises:
            httpx.HTTPStatusError: Si la petición falla después de todos los reintentos
        """
        for attempt in range(max_retries):
            try:
                # Esperar si es necesario para rate limiting
                await self._wait_for_rate_limit()
                
                # Hacer la petición
                response = await self.client.get(url)
                response.raise_for_status()
                json_response = response.json()

                # Guardar en S3 de forma asíncrona con el contexto del jugador
                await self._save_to_s3(url, json_response, context_identifier)

                return json_response
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limited - esperar y reintentar
                    retry_after = int(e.response.headers.get('Retry-After', 2))
                    wait_time = retry_after if attempt == 0 else retry_after * (2 ** attempt)
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise
                else:
                    # Otro error HTTP - no reintentar
                    raise
        
        # Esto no debería alcanzarse, pero por si acaso
        raise Exception(f"Failed to make request after {max_retries} attempts")
    
    async def get_summoner_by_name(
        self,
        game_name: str,
        tag_line: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene información de un invocador por su nombre de juego y tag.
        
        Args:
            game_name: Nombre del invocador (ej: "Faker")
            tag_line: Tag del invocador (ej: "KR1")
            region: Región del servidor (si no se especifica, usa la default)
            
        Returns:
            Información del invocador incluyendo puuid
        """
        region = region or self.default_region
        cluster = self.PLATFORM_TO_CLUSTER.get(region.lower(), "americas")
        base_url = self._get_regional_url(cluster)
        url = f"{base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        # Usar game_name y tag_line como identificador único antes de tener el puuid
        identifier = f"{game_name}-{tag_line}"
        return await self._make_request(url, context_identifier=identifier)
    
    async def get_summoner_by_puuid(
        self,
        puuid: str,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene información de un invocador por PUUID.
        
        Args:
            puuid: PUUID del invocador
            region: Región del servidor
            
        Returns:
            Información del invocador
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return await self._make_request(url, context_identifier=s3_context)
    
    async def get_champion_masteries(
        self,
        puuid: str,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las maestrías de campeones de un jugador.
        
        Args:
            puuid: PUUID del jugador
            region: Región del servidor
            
        Returns:
            Lista de maestrías de campeones
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        return await self._make_request(url, context_identifier=s3_context)
    
    async def get_champion_mastery(
        self,
        puuid: str,
        champion_id: int,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la maestría de un campeón específico.
        
        Args:
            puuid: PUUID del jugador
            champion_id: ID del campeón
            region: Región del servidor
            
        Returns:
            Maestría del campeón
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}"
        return await self._make_request(url, context_identifier=s3_context)
    
    async def get_top_champion_masteries(
        self,
        puuid: str,
        count: int = 3,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las top maestrías de campeones de un jugador.
        
        Args:
            puuid: PUUID del jugador
            count: Número de campeones a retornar (max 10)
            region: Región del servidor
            
        Returns:
            Lista de top maestrías
        """
        region = region or self.default_region
        count = min(count, 10)  # Límite de la API
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count={count}"
        return await self._make_request(url, context_identifier=s3_context)
    
    async def get_mastery_score(
        self,
        puuid: str,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> int:
        """
        Obtiene la puntuación total de maestría de un jugador.
        
        Args:
            puuid: PUUID del jugador
            region: Región del servidor
            
        Returns:
            Puntuación total de maestría
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/champion-mastery/v4/scores/by-puuid/{puuid}"
        return await self._make_request(url, context_identifier=s3_context)
    
    # ===== SUMMONER API v4 =====
    
    async def get_summoner_by_summoner_id(
        self,
        summoner_id: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene información de un invocador por Summoner ID.
        
        Args:
            summoner_id: Summoner ID del jugador
            region: Región del servidor
            
        Returns:
            Información del invocador
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/summoner/v4/summoners/{summoner_id}"
        return await self._make_request(url)
    
    # ===== LEAGUE API v4 =====
    
    async def get_league_entries_by_summoner(
        self,
        summoner_id: str,
        region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las entradas de liga (ranked) de un invocador por Summoner ID.
        DEPRECATED: Usar get_league_entries_by_puuid en su lugar.
        
        Args:
            summoner_id: Summoner ID del jugador
            region: Región del servidor
            
        Returns:
            Lista de entradas de liga (Solo/Duo, Flex, etc.)
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/league/v4/entries/by-summoner/{summoner_id}"
        return await self._make_request(url)
    
    async def get_league_entries_by_puuid(
        self,
        puuid: str,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las entradas de liga (ranked) de un invocador por PUUID.
        Método actualizado que usa el nuevo endpoint de Riot API.
        
        Args:
            puuid: PUUID del jugador
            region: Región del servidor
            
        Returns:
            Lista de entradas de liga (Solo/Duo, Flex, etc.)
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/league/v4/entries/by-puuid/{puuid}"
        return await self._make_request(url, context_identifier=s3_context)
    
    async def get_challenger_league(
        self,
        queue: str = "RANKED_SOLO_5x5",
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la liga Challenger.
        
        Args:
            queue: Tipo de cola (RANKED_SOLO_5x5, RANKED_FLEX_SR)
            region: Región del servidor
            
        Returns:
            Información de la liga Challenger
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/league/v4/challengerleagues/by-queue/{queue}"
        return await self._make_request(url)
    
    async def get_grandmaster_league(
        self,
        queue: str = "RANKED_SOLO_5x5",
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la liga Grandmaster.
        
        Args:
            queue: Tipo de cola (RANKED_SOLO_5x5, RANKED_FLEX_SR)
            region: Región del servidor
            
        Returns:
            Información de la liga Grandmaster
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/league/v4/grandmasterleagues/by-queue/{queue}"
        return await self._make_request(url)
    
    async def get_master_league(
        self,
        queue: str = "RANKED_SOLO_5x5",
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la liga Master.
        
        Args:
            queue: Tipo de cola (RANKED_SOLO_5x5, RANKED_FLEX_SR)
            region: Región del servidor
            
        Returns:
            Información de la liga Master
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/league/v4/masterleagues/by-queue/{queue}"
        return await self._make_request(url)
    
    # ===== MATCH API v5 =====
    
    async def get_match_history(
        self,
        puuid: str,
        count: int = 20,
        start: int = 0,
        region: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        s3_context: Optional[str] = None
    ) -> List[str]:
        """
        Obtiene el historial de IDs de partidas de un jugador.
        
        Args:
            puuid: PUUID del jugador
            count: Número de partidas a retornar (max 100)
            start: Índice de inicio
            region: Región del servidor
            start_time: Timestamp epoch en SEGUNDOS (filtra partidas después de este tiempo)
            end_time: Timestamp epoch en SEGUNDOS (filtra partidas antes de este tiempo)
            
        Returns:
            Lista de IDs de partidas
        """
        region = region or self.default_region
        cluster = self.PLATFORM_TO_CLUSTER.get(region.lower(), "americas")
        base_url = self._get_regional_url(cluster)
        url = f"{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        
        # Añadir filtros de tiempo si se especifican
        if start_time:
            url += f"&startTime={start_time}"
        if end_time:
            url += f"&endTime={end_time}"
        
        return await self._make_request(url, context_identifier=s3_context)
    
    async def get_match_details(
        self,
        match_id: str,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene los detalles completos de una partida.
        
        Args:
            match_id: ID de la partida
            region: Región del servidor
            
        Returns:
            Información detallada de la partida
        """
        region = region or self.default_region
        cluster = self.PLATFORM_TO_CLUSTER.get(region.lower(), "americas")
        base_url = self._get_regional_url(cluster)
        url = f"{base_url}/lol/match/v5/matches/{match_id}"
        return await self._make_request(url, context_identifier=s3_context)
    
    async def get_match_timeline(
        self,
        match_id: str,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la línea de tiempo detallada de una partida.
        
        Args:
            match_id: ID de la partida
            region: Región del servidor
            
        Returns:
            Timeline de la partida con eventos minuto a minuto
        """
        region = region or self.default_region
        cluster = self.PLATFORM_TO_CLUSTER.get(region.lower(), "americas")
        base_url = self._get_regional_url(cluster)
        url = f"{base_url}/lol/match/v5/matches/{match_id}/timeline"
        return await self._make_request(url, context_identifier=s3_context)
    
    # ===== SPECTATOR API v5 =====
    
    async def get_current_game(
        self,
        puuid: str,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene información de la partida en curso de un jugador.
        
        Args:
            puuid: PUUID del jugador
            region: Región del servidor
            
        Returns:
            Información de la partida en curso
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/spectator/v5/active-games/by-summoner/{puuid}"
        return await self._make_request(url, context_identifier=s3_context)
    
    async def get_featured_games(
        self,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene una lista de partidas destacadas actualmente en curso.
        
        Args:
            region: Región del servidor
            
        Returns:
            Lista de partidas destacadas
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/spectator/v5/featured-games"
        return await self._make_request(url)
    
    # ===== CHAMPION API v3 =====
    
    async def get_champion_rotations(
        self,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la rotación de campeones gratuitos de la semana.
        
        Args:
            region: Región del servidor
            
        Returns:
            IDs de campeones en rotación gratuita
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/platform/v3/champion-rotations"
        return await self._make_request(url)
    
    # ===== LOL CHALLENGES API v1 =====
    
    async def get_challenges_config(
        self,
        region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de todos los desafíos básicos.
        
        Args:
            region: Región del servidor
            
        Returns:
            Lista de configuraciones de desafíos
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/challenges/v1/challenges/config"
        return await self._make_request(url)
    
    async def get_challenge_config(
        self,
        challenge_id: int,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la configuración de un desafío específico.
        
        Args:
            challenge_id: ID del desafío
            region: Región del servidor
            
        Returns:
            Configuración del desafío
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/challenges/v1/challenges/{challenge_id}/config"
        return await self._make_request(url)
    
    async def get_challenge_leaderboard(
        self,
        challenge_id: int,
        level: str = "CHALLENGER",
        limit: int = 10,
        region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la tabla de líderes de un desafío específico.
        
        Args:
            challenge_id: ID del desafío
            level: Nivel del leaderboard (MASTER, GRANDMASTER, CHALLENGER)
            limit: Límite de resultados
            region: Región del servidor
            
        Returns:
            Lista de jugadores en el leaderboard
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/challenges/v1/challenges/{challenge_id}/leaderboards/by-level/{level}"
        if limit:
            url += f"?limit={limit}"
        return await self._make_request(url)
    
    async def get_challenge_percentiles(
        self,
        challenge_id: int,
        region: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Obtiene los percentiles de un desafío específico.
        
        Args:
            challenge_id: ID del desafío
            region: Región del servidor
            
        Returns:
            Percentiles del desafío
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/challenges/v1/challenges/{challenge_id}/percentiles"
        return await self._make_request(url)
    
    async def get_player_challenges(
        self,
        puuid: str,
        region: Optional[str] = None,
        s3_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene todos los desafíos de un jugador por PUUID.
        
        Args:
            puuid: PUUID del jugador
            region: Región del servidor
            
        Returns:
            Datos completos de desafíos del jugador incluyendo:
            - Puntos totales
            - Puntos por categoría
            - Lista de todos los desafíos con progreso
            - Percentiles
            - Niveles alcanzados
        """
        region = region or self.default_region
        base_url = self._get_platform_url(region)
        url = f"{base_url}/lol/challenges/v1/player-data/{puuid}"
        return await self._make_request(url, context_identifier=s3_context)

