#!/usr/bin/env bash
# build.sh - Script de construcción para Render.com
# Marco0425 - DinnerSchool - 2025-08-19 04:08:39 UTC

set -o errexit  # exit on error

echo "🚀 Iniciando build de DinnerSchool..."
echo "📅 $(date)"
echo "👤 Usuario: Marco0425"

# Instalar dependencias del sistema para PostgreSQL
echo "🔧 Instalando dependencias del sistema..."
apt-get update
apt-get install -y postgresql-client libpq-dev gcc python3-dev

# Actualizar pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Instalar wheel primero
echo "🛠️ Instalando wheel..."
pip install wheel

# Instalar psycopg2 específicamente
echo "🐘 Instalando PostgreSQL adapter..."
pip install psycopg2==2.9.7

# Instalar resto de dependencias
echo "📦 Instalando dependencias restantes..."
pip install -r requirements.txt

echo "🔧 Configurando Django..."
cd DinnerSchool

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --no-input

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "✅ Build completado exitosamente!"
echo "📊 Estadísticas del deploy:"
echo "   - Python version: $(python --version)"
echo "   - Django version: $(python -c 'import django; print(django.get_version())')"
echo "   - PostgreSQL: ✅ Conectado"