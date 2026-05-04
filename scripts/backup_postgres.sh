#!/usr/bin/env sh
set -eu

OUTPUT_DIR="${1:-./backups}"
TIMESTAMP="$(date +"%Y%m%d-%H%M%S")"
mkdir -p "$OUTPUT_DIR"

POSTGRES_USER="${POSTGRES_USER:-photoengine}"
POSTGRES_DB="${POSTGRES_DB:-photoengine}"
OUTPUT_FILE="$OUTPUT_DIR/photoengine-db-$TIMESTAMP.sql"

docker compose -f docker-compose.prod.yml exec -T db \
    pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$OUTPUT_FILE"

echo "Database backup written to $OUTPUT_FILE"
