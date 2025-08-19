#!/usr/bin/env bash
# build.sh - Script de construcción para Render.com
# Marco0425 - DinnerSchool - 2025-08-19 04:16:10 UTC

set -o errexit  # exit on error

echo "🚀 Iniciando build de DinnerSchool..."
echo "📅 $(date)"
echo "👤 Usuario: Marco0425"
echo "🐍 Python: $(python --version)"

# Actualizar pip y setuptools
echo "📦 Actualizando herramientas de Python..."
python -m pip install --upgrade pip setuptools wheel

# Instalar dependencias
echo "📦 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

echo "🔧 Configurando Django..."
cd DinnerSchool

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --no-input

# Crear superusuario si no existe
echo "👤 Configurando usuario administrador..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dinnerschool.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('✅ Superusuario ya existe')
"

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "✅ Build completado exitosamente!"
echo "📊 Estadísticas del deploy:"
echo "   - Python: $(python --version)"
echo "   - Django: $(python -c 'import django; print(django.get_version())')"
echo "   - Database: ✅ PostgreSQL via Render"
echo "   - Static files: ✅ Configurados"
echo "🌐 App estará disponible en: https://dinnerschool-marco.onrender.com"