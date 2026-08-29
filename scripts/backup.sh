#!/bin/sh
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f $ROOT/docker-compose.yml"
mkdir -p "$ROOT/backup"
STAMP=$(date +%Y%m%d-%H%M%S)

case "${DATABASE_URL:-}" in
  postgresql*)
    echo "当前使用外部 PostgreSQL，请直接在数据库服务器上执行 pg_dump 备份。"
    exit 1
    ;;
  *)
    FILE="$ROOT/backup/sqlite-$STAMP.db"
    $COMPOSE exec -T app python - <<'PY'
import os, sqlite3
from urllib.parse import urlparse
url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:////data/app/xhs_selection.db")
path = urlparse(url.replace("+aiosqlite", "")).path
src = sqlite3.connect(path)
dst = sqlite3.connect("/tmp/xhs-backup.db")
src.backup(dst)
dst.close()
src.close()
PY
    $COMPOSE cp app:/tmp/xhs-backup.db "$FILE"
    $COMPOSE exec -T app rm /tmp/xhs-backup.db
    echo "$FILE"
    ;;
esac
