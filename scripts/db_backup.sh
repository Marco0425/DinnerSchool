#!/usr/bin/env bash
set -euo pipefail

# Respalda la base de datos del servicio "db" de docker-compose activo.
# Uso: ./scripts/db_backup.sh [nombre_opcional]

cd "$(dirname "$0")/.."

if [ -f .env.docker ]; then
  export $(grep -v '^#' .env.docker | grep -E '^(DB_NAME|DB_USER|DB_PASSWORD)=' | xargs)
fi

: "${DB_NAME:?Falta DB_NAME (revisa .env.docker)}"
: "${DB_USER:?Falta DB_USER (revisa .env.docker)}"

mkdir -p backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
NOMBRE="${1:-dinnerschool}"
ARCHIVO="backups/${NOMBRE}_${TIMESTAMP}.dump"

echo "Respaldando $DB_NAME desde el contenedor 'db' -> $ARCHIVO"
docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$ARCHIVO"

echo "Listo: $ARCHIVO ($(du -h "$ARCHIVO" | cut -f1))"
