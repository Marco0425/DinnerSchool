#!/usr/bin/env bash
# build.sh - Script de construcción para Render.com
# Marco0425 - DinnerSchool

set -o errexit  # exit on error

echo "🚀 Iniciando build de DinnerSchool..."

# Instalar dependencias
echo "📦 Instalando dependencias Python..."
pip install -r requirements.txt

echo "🔧 Configurando Django..."
cd DinnerSchool

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --no-input

echo "✅ Build completado exitosamente!"