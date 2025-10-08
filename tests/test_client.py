"""Tests para el cliente de Riot API."""

import pytest
from lol_wrapper.client import RiotAPIClient


@pytest.fixture
def client():
    """Fixture del cliente."""
    return RiotAPIClient("test_api_key", default_region="na1")


def test_client_initialization(client):
    """Test de inicialización del cliente."""
    assert client.api_key == "test_api_key"
    assert client.default_region == "na1"


def test_get_platform_url(client):
    """Test de obtención de URL de plataforma."""
    url = client._get_platform_url("na1")
    assert url == "https://na1.api.riotgames.com"
    
    url = client._get_platform_url("kr")
    assert url == "https://kr.api.riotgames.com"


def test_get_platform_url_invalid_region(client):
    """Test de región inválida."""
    with pytest.raises(ValueError):
        client._get_platform_url("invalid")


def test_get_regional_url(client):
    """Test de obtención de URL regional."""
    url = client._get_regional_url("americas")
    assert url == "https://americas.api.riotgames.com"
    
    url = client._get_regional_url("asia")
    assert url == "https://asia.api.riotgames.com"


def test_get_regional_url_invalid_cluster(client):
    """Test de cluster regional inválido."""
    with pytest.raises(ValueError):
        client._get_regional_url("invalid")


def test_platform_to_cluster_mapping(client):
    """Test de mapeo de plataforma a cluster."""
    assert client.PLATFORM_TO_CLUSTER["na1"] == "americas"
    assert client.PLATFORM_TO_CLUSTER["kr"] == "asia"
    assert client.PLATFORM_TO_CLUSTER["euw1"] == "europe"
    assert client.PLATFORM_TO_CLUSTER["sg2"] == "sea"


@pytest.mark.asyncio
async def test_client_cleanup(client):
    """Test de limpieza del cliente."""
    await client.close()
    assert client.client.is_closed

