#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 path/to/backup.sql" >&2
    exit 1
fi

INPUT_FILE="$1"
POSTGRES_USER="${POSTGRES_USER:-photoengine}"
POSTGRES_DB="${POSTGRES_DB:-photoengine}"

docker compose -f docker-compose.prod.yml exec -T db \
    psql -U "$POSTGRES_USER" "$POSTGRES_DB" < "$INPUT_FILE"

echo "Database restore completed from $INPUT_FILE"
