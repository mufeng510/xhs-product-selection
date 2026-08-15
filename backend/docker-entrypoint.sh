#!/bin/sh
set -eu
echo "waiting for postgres..."
python - <<'PY'
import os, time
from urllib.parse import urlparse
url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://xhs:change_me@postgres:5432/xhs_selection")
parsed = urlparse(url.replace("postgresql+asyncpg", "postgresql"))
host = parsed.hostname or "postgres"
port = parsed.port or 5432
import socket
for i in range(60):
    try:
        s = socket.create_connection((host, port), 2)
        s.close()
        break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("postgres not reachable")
PY
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
