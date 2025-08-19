#!/usr/bin/env python
"""
Script para migrar datos de SQLite a PostgreSQL
Para el proyecto DinnerSchool
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connections, transaction
from django.apps import apps
import sqlite3
import psycopg2
from urllib.parse import urlparse

def setup_django():
    """Configurar Django para el script"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    django.setup()

def export_sqlite_data():
    """Exportar datos de SQLite"""
    print("📤 Exportando datos de SQLite...")
    
    # Obtener conexión SQLite
    sqlite_conn = connections['default']
    
    if sqlite_conn.vendor != 'sqlite':
        print("❌ Error: La base de datos actual no es SQLite")
        return None
    
    data = {}
    
    # Obtener todos los modelos
    for model in apps.get_models():
        if model._meta.app_label in ['core', 'comedor']:
            table_name = model._meta.db_table
            print(f"  📋 Exportando tabla: {table_name}")
            
            objects = model.objects.all()
            data[model] = list(objects.values())
            print(f"     ✅ {len(data[model])} registros exportados")
    
    return data

def import_postgresql_data(data, database_url):
    """Importar datos a PostgreSQL"""
    print("📥 Importando datos a PostgreSQL...")
    
    # Parsear URL de PostgreSQL
    url = urlparse(database_url)
    
    # Configurar conexión PostgreSQL temporalmente
    postgres_config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': url.path[1:],
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': url.port,
    }
    
    # Actualizar configuración de base de datos
    from django.conf import settings
    settings.DATABASES['default'] = postgres_config
    
    # Crear tablas en PostgreSQL
    print("🔨 Creando tablas en PostgreSQL...")
    execute_from_command_line(['manage.py', 'migrate', '--verbosity=0'])
    
    # Importar datos
    for model, records in data.items():
        if records:  # Solo si hay datos
            table_name = model._meta.db_table
            print(f"  📋 Importando tabla: {table_name}")
            
            try:
                with transaction.atomic():
                    for record in records:
                        # Remover 'id' para evitar conflictos de auto-increment
                        if 'id' in record:
                            del record['id']
                        model.objects.create(**record)
                
                print(f"     ✅ {len(records)} registros importados")
            
            except Exception as e:
                print(f"     ❌ Error importando {table_name}: {e}")

def migrate_to_postgresql(database_url):
    """Función principal de migración"""
    print("🚀 Iniciando migración de SQLite a PostgreSQL")
    print("=" * 50)
    
    try:
        # 1. Exportar datos de SQLite
        data = export_sqlite_data()
        
        if not data:
            print("❌ Error: No se pudieron exportar los datos de SQLite")
            return False
        
        # 2. Verificar conexión PostgreSQL
        print("\n🔍 Verificando conexión PostgreSQL...")
        url = urlparse(database_url)
        
        try:
            conn = psycopg2.connect(
                host=url.hostname,
                port=url.port,
                user=url.username,
                password=url.password,
                database=url.path[1:]
            )
            conn.close()
            print("✅ Conexión PostgreSQL exitosa")
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {e}")
            return False
        
        # 3. Importar datos a PostgreSQL
        import_postgresql_data(data, database_url)
        
        print("\n🎉 Migración completada exitosamente!")
        print("📝 Recuerda actualizar tu variable DATABASE_URL en producción")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python migrate_to_postgres.py <DATABASE_URL>")
        print("Ejemplo: python migrate_to_postgres.py postgresql://user:pass@localhost:5432/dinnerschool")
        sys.exit(1)
    
    database_url = sys.argv[1]
    
    # Configurar Django
    setup_django()
    
    # Ejecutar migración
    success = migrate_to_postgresql(database_url)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)