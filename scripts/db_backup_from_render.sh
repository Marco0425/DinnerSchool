#!/usr/bin/env bash
set -euo pipefail

# Respalda la base de PRODUCCIÓN (Render) a un archivo .dump local.
# Requiere la External Database URL de Render (no la interna).
# Uso:
#   export RENDER_DATABASE_URL="postgresql://usuario:password@host.render.com/dinnerschool_db"
#   ./scripts/db_backup_from_render.sh

cd "$(dirname "$0")/.."

: "${RENDER_DATABASE_URL:?Exporta RENDER_DATABASE_URL con la External Database URL de Render antes de correr esto}"

mkdir -p backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVO="backups/produccion_render_${TIMESTAMP}.dump"

echo "Respaldando la base de Render -> $ARCHIVO"
docker run --rm postgres:17-alpine \
  pg_dump "$RENDER_DATABASE_URL" -Fc > "$ARCHIVO"

echo "Listo: $ARCHIVO ($(du -h "$ARCHIVO" | cut -f1))"
echo "Guárdalo en un lugar seguro fuera del repo (contiene datos reales de alumnos/tutores)."
