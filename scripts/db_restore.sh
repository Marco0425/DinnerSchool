#!/usr/bin/env bash
set -euo pipefail

# Restaura un backup .dump en el servicio "db" de docker-compose activo.
# BORRA los datos actuales de esa base antes de restaurar.
# Uso: ./scripts/db_restore.sh backups/archivo.dump

cd "$(dirname "$0")/.."

ARCHIVO="${1:?Uso: ./scripts/db_restore.sh backups/archivo.dump}"
[ -f "$ARCHIVO" ] || { echo "No existe el archivo: $ARCHIVO"; exit 1; }

if [ -f .env.docker ]; then
  export $(grep -v '^#' .env.docker | grep -E '^(DB_NAME|DB_USER|DB_PASSWORD)=' | xargs)
fi
: "${DB_NAME:?Falta DB_NAME (revisa .env.docker)}"
: "${DB_USER:?Falta DB_USER (revisa .env.docker)}"

echo "Esto va a BORRAR y reemplazar los datos de '$DB_NAME' en el contenedor 'db' de $(pwd)."
read -p "¿Seguro que este es el ambiente correcto? Escribe 'si' para continuar: " CONFIRMA
[ "$CONFIRMA" = "si" ] || { echo "Cancelado."; exit 1; }

echo "Asegurando que el servicio db esté arriba..."
docker compose up -d db

echo "Esperando a que postgres esté listo..."
until docker compose exec -T db pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; do
  sleep 1
done

echo "Reiniciando el schema 'public' para evitar conflictos de dependencias..."
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "Restaurando $ARCHIVO -> $DB_NAME ..."
cat "$ARCHIVO" | docker compose exec -T db pg_restore -U "$DB_USER" -d "$DB_NAME" \
  --no-owner --no-privileges

echo "Restauración completa. Corriendo migraciones por si faltara alguna..."
docker compose exec -T web python manage.py migrate --no-input || true

echo "Listo. Revisa la app para confirmar que los datos cargaron bien."
