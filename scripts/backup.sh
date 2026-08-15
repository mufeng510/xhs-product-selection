#!/bin/sh
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/backup"
STAMP=$(date +%Y%m%d-%H%M%S)
FILE="$ROOT/backup/postgres-$STAMP.sql"
docker compose -f "$ROOT/docker-compose.yml" exec -T postgres pg_dump -U "${POSTGRES_USER:-xhs}" "${POSTGRES_DB:-xhs_selection}" > "$FILE"
echo "$FILE"
