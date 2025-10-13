"""Cliente para Data Dragon - CDN de assets de Riot Games.

Data Dragon proporciona acceso a todas las imágenes, datos estáticos y assets
del juego sin consumir rate limits de la API.
"""

import httpx
from typing import Dict, Any, Optional, List


class DataDragonClient:
    """Cliente para acceder a Data Dragon (CDN de assets de Riot)."""
    
    # URL base de Data Dragon
    BASE_URL = "https://ddragon.leagueoflegends.com"
    
    # Cache de la versión más reciente
    _latest_version: Optional[str] = None
    
    def __init__(self):
        """Inicializa el cliente de Data Dragon."""
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def close(self):
        """Cierra el cliente HTTP."""
        await self.client.aclose()
    
    async def get_versions(self) -> List[str]:
        """
        Obtiene todas las versiones disponibles de Data Dragon.
        
        Returns:
            Lista de versiones ordenadas (más reciente primero)
        """
        url = f"{self.BASE_URL}/api/versions.json"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    async def get_latest_version(self) -> str:
        """
        Obtiene la versión más reciente de Data Dragon.
        
        Returns:
            String con la versión más reciente (ej: "14.1.1")
        """
        if self._latest_version is None:
            versions = await self.get_versions()
            self._latest_version = versions[0]
        return self._latest_version
    
    async def get_champions_data(self, version: Optional[str] = None, locale: str = "es_MX") -> Dict[str, Any]:
        """
        Obtiene todos los datos de campeones para una versión específica.
        
        Args:
            version: Versión de Data Dragon (ej: "14.1.1"). Si no se especifica, usa la más reciente.
            locale: Idioma de los datos (es_MX, es_ES, en_US, etc.)
            
        Returns:
            Diccionario con todos los datos de campeones
        """
        if version is None:
            version = await self.get_latest_version()
        
        url = f"{self.BASE_URL}/cdn/{version}/data/{locale}/champion.json"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    async def get_champion_data(
        self, 
        champion_name: str, 
        version: Optional[str] = None,
        locale: str = "es_MX"
    ) -> Dict[str, Any]:
        """
        Obtiene datos detallados de un campeón específico.
        
        Args:
            champion_name: Nombre del campeón (ej: "Ahri", "Jinx")
            version: Versión de Data Dragon
            locale: Idioma de los datos
            
        Returns:
            Datos completos del campeón incluyendo habilidades, stats, etc.
        """
        if version is None:
            version = await self.get_latest_version()
        
        url = f"{self.BASE_URL}/cdn/{version}/data/{locale}/champion/{champion_name}.json"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_champion_icon_url(self, champion_name: str, version: Optional[str] = None) -> str:
        """
        Obtiene la URL del ícono de un campeón.
        
        Args:
            champion_name: Nombre del campeón (ej: "Ahri", "Jinx")
            version: Versión de Data Dragon (si no se especifica, usa "latest")
            
        Returns:
            URL completa de la imagen del campeón
            
        Example:
            https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Ahri.png
        """
        version = version or "latest"
        return f"{self.BASE_URL}/cdn/{version}/img/champion/{champion_name}.png"
    
    def get_champion_splash_url(self, champion_name: str, skin_num: int = 0) -> str:
        """
        Obtiene la URL del splash art de un campeón.
        
        Args:
            champion_name: Nombre del campeón (ej: "Ahri", "Jinx")
            skin_num: Número de skin (0 = skin por defecto)
            
        Returns:
            URL completa del splash art
            
        Example:
            https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ahri_0.jpg
        """
        return f"{self.BASE_URL}/cdn/img/champion/splash/{champion_name}_{skin_num}.jpg"
    
    def get_champion_loading_url(self, champion_name: str, skin_num: int = 0) -> str:
        """
        Obtiene la URL de la imagen de carga de un campeón.
        
        Args:
            champion_name: Nombre del campeón
            skin_num: Número de skin (0 = skin por defecto)
            
        Returns:
            URL completa de la imagen de carga
            
        Example:
            https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Ahri_0.jpg
        """
        return f"{self.BASE_URL}/cdn/img/champion/loading/{champion_name}_{skin_num}.jpg"
    
    def get_champion_square_url(self, champion_name: str, version: Optional[str] = None) -> str:
        """
        Obtiene la URL de la imagen cuadrada pequeña del campeón.
        Útil para minimaps y displays compactos.
        
        Args:
            champion_name: Nombre del campeón
            version: Versión de Data Dragon (si no se especifica, usa "latest")
            
        Returns:
            URL completa de la imagen cuadrada
        """
        version = version or "latest"
        return f"{self.BASE_URL}/cdn/{version}/img/champion/{champion_name}.png"
    
    def get_profile_icon_url(self, icon_id: int, version: Optional[str] = None) -> str:
        """
        Obtiene la URL de un ícono de perfil.
        
        Args:
            icon_id: ID del ícono de perfil
            version: Versión de Data Dragon
            
        Returns:
            URL completa del ícono de perfil
        """
        version = version or "latest"
        return f"{self.BASE_URL}/cdn/{version}/img/profileicon/{icon_id}.png"
    
    def get_item_icon_url(self, item_id: int, version: Optional[str] = None) -> str:
        """
        Obtiene la URL del ícono de un objeto/item.
        
        Args:
            item_id: ID del objeto
            version: Versión de Data Dragon
            
        Returns:
            URL completa del ícono del objeto
        """
        version = version or "latest"
        return f"{self.BASE_URL}/cdn/{version}/img/item/{item_id}.png"
    
    def get_spell_icon_url(self, spell_name: str, version: Optional[str] = None) -> str:
        """
        Obtiene la URL del ícono de un hechizo.
        
        Args:
            spell_name: Nombre del hechizo (ej: "Flash", "Ignite")
            version: Versión de Data Dragon
            
        Returns:
            URL completa del ícono del hechizo
        """
        version = version or "latest"
        return f"{self.BASE_URL}/cdn/{version}/img/spell/{spell_name}.png"
    
    async def get_champion_id_mapping(self, version: Optional[str] = None) -> Dict[int, str]:
        """
        Obtiene un mapeo de champion_id -> champion_name.
        Útil para convertir IDs numéricos en nombres para URLs.
        
        Args:
            version: Versión de Data Dragon
            
        Returns:
            Diccionario {champion_id: champion_name}
        """
        champions_data = await self.get_champions_data(version)
        
        # Crear mapeo de ID -> nombre
        id_to_name = {}
        for champ_name, champ_data in champions_data["data"].items():
            champion_id = int(champ_data["key"])
            id_to_name[champion_id] = champ_name
        
        return id_to_name
    
    async def get_champion_name_from_id(self, champion_id: int, version: Optional[str] = None) -> str:
        """
        Convierte un champion_id numérico en su nombre de Data Dragon.
        
        Args:
            champion_id: ID numérico del campeón (ej: 103 para Ahri)
            version: Versión de Data Dragon
            
        Returns:
            Nombre del campeón para usar en URLs de Data Dragon
        """
        mapping = await self.get_champion_id_mapping(version)
        return mapping.get(champion_id, "Unknown")
    
    async def get_champion_urls(
        self, 
        champion_id: int, 
        version: Optional[str] = None,
        skin_num: int = 0
    ) -> Dict[str, str]:
        """
        Obtiene todas las URLs relevantes de un campeón de una vez.
        
        Args:
            champion_id: ID numérico del campeón
            version: Versión de Data Dragon
            skin_num: Número de skin
            
        Returns:
            Diccionario con todas las URLs del campeón:
            {
                "icon": "url...",
                "splash": "url...",
                "loading": "url...",
                "square": "url...",
                "name": "champion_name"
            }
        """
        champion_name = await self.get_champion_name_from_id(champion_id, version)
        
        return {
            "name": champion_name,
            "icon": self.get_champion_icon_url(champion_name, version),
            "splash": self.get_champion_splash_url(champion_name, skin_num),
            "loading": self.get_champion_loading_url(champion_name, skin_num),
            "square": self.get_champion_square_url(champion_name, version)
        }

