#!/usr/bin/env bash
# build.sh - Script de construcción para Render.com
# Marco0425 - DinnerSchool - 2025-08-19 04:22:45 UTC

set -o errexit  # exit on error

echo "🚀 Iniciando build de DinnerSchool..."
echo "📅 $(date)"
echo "👤 Usuario: Marco0425"
echo "🐍 Python: $(python --version)"

# Actualizar pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Instalar setuptools y wheel primero
echo "🛠️ Instal ando herramientas de construcción..."
pip install --upgrade setuptools wheel

# Instalar dependencias una por una para debug
echo "🔧 Instalando Django..."
pip install Django==4.1.13

echo "🌐 Instalando gunicorn..."
pip install gunicorn==20.1.0

echo "📦 Instalando whitenoise..."
pip install whitenoise==6.4.0

echo "🌍 Instalando python-dotenv..."
pip install python-dotenv==1.0.0

echo "🌍 Instalando requerimientos..."
pip install -r DinnerSchool/requirements.txt

echo "🔧 Configurando Django..."
cd DinnerSchool

# Verificar estructura
echo "📁 Estructura del proyecto:"
ls -la

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --no-input

# Crear superusuario
echo "👤 Configurando administrador..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dinnerschool.com', 'admin123')
    print('✅ Superusuario creado: admin/admin123')
else:
    print('✅ Superusuario ya existe')
" || echo "⚠️ No se pudo crear superusuario (normal en primera ejecución)"

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --no-input --clear

python -c "import mysite.wsgi; print('✅ Importación exitosa')"

echo "✅ Build completado exitosamente!"
echo ""
echo "🎉 DinnerSchool está listo para deploy!"
echo "📊 Resumen:"
echo "   - Python: $(python --version)"
echo "   - Django: $(python -c 'import django; print(django.get_version())')"
echo "   - Database: PostgreSQL (Render)"
echo "   - Admin: admin / admin123"
echo ""
echo "🌐 URL: https://dinnerschool.onrender.com"
echo "🔐 Admin: https://dinnerschool.onrender.com/admin/"