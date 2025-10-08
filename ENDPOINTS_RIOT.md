# Endpoints de la API de Riot Games

Documentación completa de los endpoints disponibles en la API de Riot Games.

## Tabla de Contenidos

- [Account API (v1)](#account-api-v1)
- [Champion Mastery API (v4)](#champion-mastery-api-v4)
- [Champion API (v3)](#champion-api-v3)
- [Clash API (v1)](#clash-api-v1)
- [League EXP API (v4)](#league-exp-api-v4)
- [League API (v4)](#league-api-v4)
- [LOL Challenges API (v1)](#lol-challenges-api-v1)
- [LOL RSO Match API (v1)](#lol-rso-match-api-v1)
- [LOL Status API (v4)](#lol-status-api-v4)
- [Match API (v5)](#match-api-v5)
- [Summoner API (v4)](#summoner-api-v4)
- [Spectator API (v5)](#spectator-api-v5)
- [TFT League API (v1)](#tft-league-api-v1)
- [TFT Match API (v1)](#tft-match-api-v1)
- [TFT Status API (v1)](#tft-status-api-v1)
- [TFT Summoner API (v1)](#tft-summoner-api-v1)
- [Legends of Runeterra APIs](#legends-of-runeterra-apis)
- [VALORANT APIs](#valorant-apis)
- [Tournament APIs](#tournament-apis)

---

## Account API (v1)

**Routing:** americas, asia, europe

### Endpoints:

#### GET `/riot/account/v1/accounts/by-puuid/{puuid}`
**Descripción:** Obtener cuenta por PUUID  
**Parámetros:**
- `puuid` (path, required): Player Universal Unique Identifier

**Respuesta:** `AccountDto`
```json
{
  "puuid": "string",
  "gameName": "string",
  "tagLine": "string"
}
```

#### GET `/riot/account/v1/accounts/by-puuid/{puuid}` (ESPORTS)
**Descripción:** Obtener cuenta por PUUID - ESPORTS  
**Parámetros:**
- `puuid` (path, required): Player Universal Unique Identifier

#### GET `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}`
**Descripción:** Obtener cuenta por Riot ID  
**Parámetros:**
- `gameName` (path, required): Nombre del juego
- `tagLine` (path, required): Etiqueta del jugador

**Respuesta:** `AccountDto`

#### GET `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` (ESPORTS)
**Descripción:** Obtener cuenta por Riot ID - ESPORTS

#### GET `/riot/account/v1/accounts/me`
**Descripción:** Obtener cuenta por access token  
**Headers:**
- `Authorization` (required): Bearer token

#### GET `/riot/account/v1/accounts/me` (ESPORTS)
**Descripción:** Obtener cuenta por access token - ESPORTS

#### GET `/riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}`
**Descripción:** Obtener shard activo para un jugador  
**Parámetros:**
- `game` (path, required): `val` o `lor`
- `puuid` (path, required): Player UUID

**Respuesta:** `ActiveShardDto`

#### GET `/riot/account/v1/region/by-game/{game}/by-puuid/{puuid}`
**Descripción:** Obtener región activa (lol y tft)  
**Parámetros:**
- `game` (path, required): `lol` o `tft`
- `puuid` (path, required): Player UUID

**Respuesta:** `AccountRegionDTO`
```json
{
  "puuid": "string",
  "game": "string",
  "region": "string"
}
```

---

## Champion Mastery API (v4)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}`
**Descripción:** Obtener todas las maestrías de campeón por PUUID del invocador  
**Parámetros:**
- `encryptedPUUID` (path, required): Encrypted PUUID

#### GET `/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/by-champion/{championId}`
**Descripción:** Obtener maestría de campeón específico por PUUID  
**Parámetros:**
- `encryptedPUUID` (path, required): Encrypted PUUID
- `championId` (path, required): Champion ID

#### GET `/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/top`
**Descripción:** Obtener top maestrías de campeón por PUUID  
**Parámetros:**
- `encryptedPUUID` (path, required): Encrypted PUUID
- `count` (query, optional): Número de entradas a devolver (default: 3)

#### GET `/lol/champion-mastery/v4/scores/by-puuid/{encryptedPUUID}`
**Descripción:** Obtener puntuación total de maestría por PUUID  
**Parámetros:**
- `encryptedPUUID` (path, required): Encrypted PUUID

---

## Champion API (v3)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/platform/v3/champion-rotations`
**Descripción:** Obtener rotación de campeones gratuitos (incluyendo para jugadores nuevos)  
**Sin parámetros**

**Respuesta:** `ChampionInfo`
```json
{
  "maxNewPlayerLevel": "integer",
  "freeChampionIdsForNewPlayers": ["integer"],
  "freeChampionIds": ["integer"]
}
```

---

## Clash API (v1)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/clash/v1/players/by-summoner/{summonerId}`
**Descripción:** Obtener información de Clash por ID de invocador  
**Parámetros:**
- `summonerId` (path, required): Summoner ID

**Respuesta:** Lista de `PlayerDto`

#### GET `/lol/clash/v1/teams/{teamId}`
**Descripción:** Obtener equipo de Clash por ID  
**Parámetros:**
- `teamId` (path, required): Team ID

**Respuesta:** `TeamDto`

#### GET `/lol/clash/v1/tournaments`
**Descripción:** Obtener todos los torneos Clash activos o próximos

**Respuesta:** Lista de `TournamentDto`

#### GET `/lol/clash/v1/tournaments/by-team/{teamId}`
**Descripción:** Obtener torneo por ID de equipo  
**Parámetros:**
- `teamId` (path, required): Team ID

**Respuesta:** `TournamentDto`

#### GET `/lol/clash/v1/tournaments/{tournamentId}`
**Descripción:** Obtener torneo por ID  
**Parámetros:**
- `tournamentId` (path, required): Tournament ID

**Respuesta:** `TournamentDto`

---

## League EXP API (v4)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/league-exp/v4/entries/{queue}/{tier}/{division}`
**Descripción:** Obtener todas las entradas de liga para cola, tier y división específicos  
**Parámetros:**
- `queue` (path, required): `RANKED_SOLO_5x5`, `RANKED_FLEX_SR`, `RANKED_FLEX_TT`
- `tier` (path, required): `IRON`, `BRONZE`, `SILVER`, `GOLD`, `PLATINUM`, `DIAMOND`
- `division` (path, required): `I`, `II`, `III`, `IV`
- `page` (query, optional): Número de página (default: 1)

**Respuesta:** Lista de `LeagueEntryDTO`

---

## League API (v4)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/league/v4/challengerleagues/by-queue/{queue}`
**Descripción:** Obtener liga de Challenger por cola  
**Parámetros:**
- `queue` (path, required): `RANKED_SOLO_5x5`, `RANKED_FLEX_SR`, `RANKED_FLEX_TT`

**Respuesta:** `LeagueListDTO`

#### GET `/lol/league/v4/grandmasterleagues/by-queue/{queue}`
**Descripción:** Obtener liga de Grandmaster por cola

#### GET `/lol/league/v4/masterleagues/by-queue/{queue}`
**Descripción:** Obtener liga de Master por cola

#### GET `/lol/league/v4/entries/by-summoner/{encryptedSummonerId}`
**Descripción:** Obtener entradas de liga por ID de invocador  
**Parámetros:**
- `encryptedSummonerId` (path, required): Encrypted Summoner ID

**Respuesta:** Lista de `LeagueEntryDTO`

#### GET `/lol/league/v4/entries/{queue}/{tier}/{division}`
**Descripción:** Obtener todas las entradas para una cola, tier y división  
**Parámetros:**
- `queue` (path, required)
- `tier` (path, required)
- `division` (path, required)
- `page` (query, optional)

#### GET `/lol/league/v4/leagues/{leagueId}`
**Descripción:** Obtener liga por ID  
**Parámetros:**
- `leagueId` (path, required): League ID

**Respuesta:** `LeagueListDTO`

---

## LOL Challenges API (v1)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/challenges/v1/challenges/config`
**Descripción:** Obtener lista de todos los desafíos básicos

**Respuesta:** Lista de `ChallengeConfigInfoDto`

#### GET `/lol/challenges/v1/challenges/{challengeId}/config`
**Descripción:** Obtener configuración de un desafío específico  
**Parámetros:**
- `challengeId` (path, required): Challenge ID

#### GET `/lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}`
**Descripción:** Obtener tabla de líderes de un desafío  
**Parámetros:**
- `challengeId` (path, required): Challenge ID
- `level` (path, required): `MASTER`, `GRANDMASTER`, `CHALLENGER`
- `limit` (query, optional): Límite de resultados

#### GET `/lol/challenges/v1/challenges/{challengeId}/percentiles`
**Descripción:** Obtener percentiles de un desafío  
**Parámetros:**
- `challengeId` (path, required): Challenge ID

#### GET `/lol/challenges/v1/player-data/{puuid}`
**Descripción:** Obtener datos de desafíos del jugador por PUUID  
**Parámetros:**
- `puuid` (path, required): Player PUUID

---

## LOL RSO Match API (v1)

**Plataforma:** League of Legends RSO

### Endpoints:

#### GET `/lol/rso-match/v1/matches/by-puuid/{puuid}/ids`
**Descripción:** Obtener lista de IDs de partidas por PUUID  
**Parámetros:**
- `puuid` (path, required): Player PUUID
- `startTime` (query, optional): Timestamp de inicio
- `endTime` (query, optional): Timestamp de fin
- `start` (query, optional): Índice de inicio (default: 0)
- `count` (query, optional): Número de IDs (default: 20)

#### GET `/lol/rso-match/v1/matches/{matchId}`
**Descripción:** Obtener datos de una partida por ID  
**Parámetros:**
- `matchId` (path, required): Match ID

---

## LOL Status API (v4)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/status/v4/platform-data`
**Descripción:** Obtener datos de estado de la plataforma de League of Legends

**Respuesta:** `PlatformDataDto`
```json
{
  "id": "string",
  "name": "string",
  "locales": ["string"],
  "maintenances": ["StatusDto"],
  "incidents": ["StatusDto"]
}
```

---

## Match API (v5)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/match/v5/matches/by-puuid/{puuid}/ids`
**Descripción:** Obtener lista de IDs de partidas por PUUID  
**Parámetros:**
- `puuid` (path, required): Player PUUID
- `startTime` (query, optional): Timestamp de inicio (epoch seconds)
- `endTime` (query, optional): Timestamp de fin (epoch seconds)
- `queue` (query, optional): Queue ID para filtrar
- `type` (query, optional): Tipo de partida (`ranked`, `normal`, `tourney`, `tutorial`)
- `start` (query, optional): Índice de inicio (default: 0)
- `count` (query, optional): Número de IDs (default: 20, max: 100)

**Respuesta:** Lista de strings (Match IDs)

#### GET `/lol/match/v5/matches/{matchId}`
**Descripción:** Obtener datos de una partida por ID  
**Parámetros:**
- `matchId` (path, required): Match ID

**Respuesta:** `MatchDto`

#### GET `/lol/match/v5/matches/{matchId}/timeline`
**Descripción:** Obtener timeline de una partida por ID  
**Parámetros:**
- `matchId` (path, required): Match ID

**Respuesta:** `MatchTimelineDto`

---

## Summoner API (v4)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/summoner/v4/summoners/by-account/{encryptedAccountId}`
**Descripción:** Obtener invocador por ID de cuenta cifrado  
**Parámetros:**
- `encryptedAccountId` (path, required): Encrypted Account ID

**Respuesta:** `SummonerDTO`

#### GET `/lol/summoner/v4/summoners/by-name/{summonerName}`
**Descripción:** Obtener invocador por nombre  
**Parámetros:**
- `summonerName` (path, required): Summoner Name

**Respuesta:** `SummonerDTO`

#### GET `/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}`
**Descripción:** Obtener invocador por PUUID cifrado  
**Parámetros:**
- `encryptedPUUID` (path, required): Encrypted PUUID

**Respuesta:** `SummonerDTO`

#### GET `/lol/summoner/v4/summoners/{encryptedSummonerId}`
**Descripción:** Obtener invocador por ID de invocador cifrado  
**Parámetros:**
- `encryptedSummonerId` (path, required): Encrypted Summoner ID

**Respuesta:** `SummonerDTO`
```json
{
  "id": "string",
  "accountId": "string",
  "puuid": "string",
  "name": "string",
  "profileIconId": "integer",
  "revisionDate": "long",
  "summonerLevel": "long"
}
```

#### GET `/lol/summoner/v4/summoners/me`
**Descripción:** Obtener invocador por access token (RSO)  
**Headers:**
- `Authorization` (required): Bearer token

---

## Spectator API (v5)

**Plataforma:** League of Legends

### Endpoints:

#### GET `/lol/spectator/v5/active-games/by-summoner/{encryptedPUUID}`
**Descripción:** Obtener partida activa por PUUID  
**Parámetros:**
- `encryptedPUUID` (path, required): Encrypted PUUID

**Respuesta:** `CurrentGameInfo`

#### GET `/lol/spectator/v5/featured-games`
**Descripción:** Obtener lista de partidas destacadas

**Respuesta:** `FeaturedGames`

---

## TFT League API (v1)

**Plataforma:** Teamfight Tactics

### Endpoints:

#### GET `/tft/league/v1/challenger`
**Descripción:** Obtener liga de Challenger

**Respuesta:** `LeagueListDTO`

#### GET `/tft/league/v1/grandmaster`
**Descripción:** Obtener liga de Grandmaster

#### GET `/tft/league/v1/master`
**Descripción:** Obtener liga de Master

#### GET `/tft/league/v1/entries/by-summoner/{encryptedSummonerId}`
**Descripción:** Obtener entradas de liga por ID de invocador  
**Parámetros:**
- `encryptedSummonerId` (path, required): Encrypted Summoner ID

**Respuesta:** Lista de `LeagueEntryDTO`

#### GET `/tft/league/v1/entries/{tier}/{division}`
**Descripción:** Obtener todas las entradas para un tier y división  
**Parámetros:**
- `tier` (path, required): `IRON`, `BRONZE`, `SILVER`, `GOLD`, `PLATINUM`, `DIAMOND`
- `division` (path, required): `I`, `II`, `III`, `IV`
- `page` (query, optional)

#### GET `/tft/league/v1/leagues/{leagueId}`
**Descripción:** Obtener liga por ID  
**Parámetros:**
- `leagueId` (path, required): League ID

#### GET `/tft/league/v1/rated-ladders/{queue}/top`
**Descripción:** Obtener top de la escalera clasificatoria  
**Parámetros:**
- `queue` (path, required): `RANKED_TFT`, `RANKED_TFT_TURBO`, etc.

---

## TFT Match API (v1)

**Plataforma:** Teamfight Tactics

### Endpoints:

#### GET `/tft/match/v1/matches/by-puuid/{puuid}/ids`
**Descripción:** Obtener lista de IDs de partidas por PUUID  
**Parámetros:**
- `puuid` (path, required): Player PUUID
- `startTime` (query, optional): Timestamp de inicio
- `endTime` (query, optional): Timestamp de fin
- `start` (query, optional): Índice de inicio (default: 0)
- `count` (query, optional): Número de IDs (default: 20)

**Respuesta:** Lista de strings (Match IDs)

#### GET `/tft/match/v1/matches/{matchId}`
**Descripción:** Obtener datos de una partida por ID  
**Parámetros:**
- `matchId` (path, required): Match ID

**Respuesta:** `MatchDto`

---

## TFT Status API (v1)

**Plataforma:** Teamfight Tactics

### Endpoints:

#### GET `/tft/status/v1/platform-data`
**Descripción:** Obtener datos de estado de la plataforma de Teamfight Tactics

**Respuesta:** `PlatformDataDto`
```json
{
  "id": "string",
  "name": "string",
  "locales": ["string"],
  "maintenances": ["StatusDto"],
  "incidents": ["StatusDto"]
}
```

---

## TFT Summoner API (v1)

**Plataforma:** Teamfight Tactics

### Endpoints:

#### GET `/tft/summoner/v1/summoners/by-account/{encryptedAccountId}`
**Descripción:** Obtener invocador por ID de cuenta cifrado

#### GET `/tft/summoner/v1/summoners/by-name/{summonerName}`
**Descripción:** Obtener invocador por nombre

#### GET `/tft/summoner/v1/summoners/by-puuid/{encryptedPUUID}`
**Descripción:** Obtener invocador por PUUID cifrado

#### GET `/tft/summoner/v1/summoners/{encryptedSummonerId}`
**Descripción:** Obtener invocador por ID de invocador cifrado

#### GET `/tft/summoner/v1/summoners/me`
**Descripción:** Obtener invocador por access token (RSO)

---

## Legends of Runeterra APIs

### LOR Deck API (v1) - RSO

#### GET `/lor/deck/v1/decks`
**Descripción:** Obtener lista de mazos del usuario autenticado  
**Headers:**
- `Authorization` (required): Bearer token

### LOR Inventory API (v1) - RSO

#### GET `/lor/inventory/v1/cards`
**Descripción:** Obtener inventario de cartas del usuario autenticado  
**Headers:**
- `Authorization` (required): Bearer token

### LOR Match API (v1)

#### GET `/lor/match/v1/matches/by-puuid/{puuid}/ids`
**Descripción:** Obtener lista de IDs de partidas por PUUID  
**Parámetros:**
- `puuid` (path, required): Player PUUID

#### GET `/lor/match/v1/matches/{matchId}`
**Descripción:** Obtener datos de una partida por ID

### LOR Ranked API (v1)

#### GET `/lor/ranked/v1/leaderboards`
**Descripción:** Obtener tabla de líderes clasificatorios

### LOR Status API (v1)

#### GET `/lor/status/v1/platform-data`
**Descripción:** Obtener datos de estado de la plataforma de Legends of Runeterra

---

## VALORANT APIs

### VAL Content API (v1)

#### GET `/val/content/v1/contents`
**Descripción:** Obtener contenido filtrado por locale  
**Parámetros:**
- `locale` (query, optional): Código de locale

### VAL Match API (v1)

#### GET `/val/match/v1/matches/{matchId}`
**Descripción:** Obtener datos de una partida por ID

#### GET `/val/match/v1/matchlists/by-puuid/{puuid}`
**Descripción:** Obtener lista de partidas por PUUID

#### GET `/val/match/v1/recent-matches/by-queue/{queue}`
**Descripción:** Obtener partidas recientes por cola

### VAL Ranked API (v1)

#### GET `/val/ranked/v1/leaderboards/by-act/{actId}`
**Descripción:** Obtener tabla de líderes por acto  
**Parámetros:**
- `actId` (path, required): Act ID
- `size` (query, optional): Número de jugadores (default: 200)
- `startIndex` (query, optional): Índice de inicio (default: 0)

### VAL Status API (v1)

#### GET `/val/status/v1/platform-data`
**Descripción:** Obtener datos de estado de la plataforma de VALORANT

### VAL Console Match API (v1)

#### GET `/val-console/match/v1/matches/{matchId}`
**Descripción:** Obtener datos de partida en consola

#### GET `/val-console/match/v1/matchlists/by-puuid/{puuid}`
**Descripción:** Obtener lista de partidas en consola por PUUID

### VAL Console Ranked API (v1)

#### GET `/val-console/ranked/v1/leaderboards/by-act/{actId}`
**Descripción:** Obtener tabla de líderes de consola por acto

---

## Tournament APIs

### Tournament API (v5)

#### GET `/lol/tournament/v5/codes`
**Descripción:** Obtener códigos de torneo  
**Query Parameters:**
- `tournamentId` (required): Tournament ID
- `count` (optional): Número de códigos

#### POST `/lol/tournament/v5/codes`
**Descripción:** Crear códigos de torneo  
**Body:** `TournamentCodeParameters`

#### GET `/lol/tournament/v5/codes/{tournamentCode}`
**Descripción:** Obtener detalles de código de torneo

#### PUT `/lol/tournament/v5/codes/{tournamentCode}`
**Descripción:** Actualizar código de torneo

#### GET `/lol/tournament/v5/lobby-events/by-code/{tournamentCode}`
**Descripción:** Obtener eventos de lobby por código de torneo

#### POST `/lol/tournament/v5/providers`
**Descripción:** Crear proveedor de torneo  
**Body:** `ProviderRegistrationParameters`

#### POST `/lol/tournament/v5/tournaments`
**Descripción:** Crear torneo  
**Body:** `TournamentRegistrationParameters`

### Tournament Stub API (v5)

Endpoints similares a Tournament API pero para pruebas en ambiente de desarrollo:

- `POST /lol/tournament-stub/v5/codes`
- `GET /lol/tournament-stub/v5/lobby-events/by-code/{tournamentCode}`
- `POST /lol/tournament-stub/v5/providers`
- `POST /lol/tournament-stub/v5/tournaments`

---

## Riftbound APIs

### Riftbound Content API (v1)

#### GET `/riftbound/content/v1/content`
**Descripción:** Obtener contenido de Riftbound

---

## Spectator TFT API (v5)

#### GET `/tft/spectator/v5/active-games/by-puuid/{encryptedPUUID}`
**Descripción:** Obtener partida activa de TFT por PUUID

#### GET `/tft/spectator/v5/featured-games`
**Descripción:** Obtener lista de partidas destacadas de TFT

---

## Notas Importantes

### Regiones y Routing

- **Regional routing:** Para APIs como Account (v1) usa rutas regionales:
  - `americas.api.riotgames.com`
  - `asia.api.riotgames.com`
  - `europe.api.riotgames.com`
  - `sea.api.riotgames.com`

- **Platform routing:** Para APIs específicas de la plataforma:
  - `br1.api.riotgames.com` (Brasil)
  - `eun1.api.riotgames.com` (Europa Nórdica y del Este)
  - `euw1.api.riotgames.com` (Europa Occidental)
  - `jp1.api.riotgames.com` (Japón)
  - `kr.api.riotgames.com` (Korea)
  - `la1.api.riotgames.com` (LAN)
  - `la2.api.riotgames.com` (LAS)
  - `na1.api.riotgames.com` (Norteamérica)
  - `oc1.api.riotgames.com` (Oceanía)
  - `ph2.api.riotgames.com` (Filipinas)
  - `ru.api.riotgames.com` (Rusia)
  - `sg2.api.riotgames.com` (Singapur)
  - `th2.api.riotgames.com` (Tailandia)
  - `tr1.api.riotgames.com` (Turquía)
  - `tw2.api.riotgames.com` (Taiwán)
  - `vn2.api.riotgames.com` (Vietnam)

### Autenticación

Todos los endpoints requieren una API key válida enviada en el header:
```
X-Riot-Token: RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Para endpoints RSO (Riot Sign-On), se requiere un Bearer token de OAuth2:
```
Authorization: Bearer <access_token>
```

### Rate Limiting

La API de Riot Games implementa rate limiting por:
- **Application rate limit:** Límite global para tu aplicación
- **Method rate limit:** Límite específico por endpoint

Los headers de respuesta incluyen información sobre rate limits:
- `X-App-Rate-Limit`
- `X-App-Rate-Limit-Count`
- `X-Method-Rate-Limit`
- `X-Method-Rate-Limit-Count`

### Códigos de Error Comunes

- `400` - Bad request
- `401` - Unauthorized (API key inválida)
- `403` - Forbidden (API key válida pero sin permisos)
- `404` - Data not found (recurso no encontrado)
- `405` - Method not allowed
- `415` - Unsupported media type
- `429` - Rate limit exceeded
- `500` - Internal server error
- `502` - Bad gateway
- `503` - Service unavailable
- `504` - Gateway timeout

---

## Referencias

- [Riot Games Developer Portal](https://developer.riotgames.com/)
- [API Documentation](https://developer.riotgames.com/apis)
- [Rate Limiting](https://developer.riotgames.com/docs/portal#web-apis_rate-limiting)

---

**Última actualización:** 2025-10-08

