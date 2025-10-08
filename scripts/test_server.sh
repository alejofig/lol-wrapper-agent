#!/bin/bash
# Script para probar el servidor MCP

echo "=== Testing League of Legends MCP Wrapper ==="
echo ""

# Verificar que existe .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Creando desde .env.example..."
    cp .env.example .env
    echo "⚠️  Por favor edita .env y añade tu RIOT_API_KEY"
    exit 1
fi

# Verificar que hay API key
if ! grep -q "RIOT_API_KEY=RGAPI" .env; then
    echo "⚠️  RIOT_API_KEY no configurada en .env"
    echo "⚠️  Por favor añade tu API key de https://developer.riotgames.com/"
    exit 1
fi

echo "✅ Configuración encontrada"
echo ""

# Verificar instalación
echo "📦 Verificando instalación..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv no está instalado"
    echo "   Instala uv desde: https://docs.astral.sh/uv/"
    exit 1
fi

echo "✅ uv instalado"
echo ""

# Ejecutar tests
echo "🧪 Ejecutando tests..."
uv run pytest tests/ -v

echo ""
echo "🚀 Iniciando servidor MCP..."
echo "   Presiona Ctrl+C para detener"
echo ""

# Iniciar servidor
uv run lol_wrapper/server.py

