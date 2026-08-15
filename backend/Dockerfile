FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl nodejs npm gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

RUN pip install --no-cache-dir . "all-in-one-aione==0.1.1" \
    && chmod +x /app/docker-entrypoint.sh

# Bake Spider_XHS next to CWD so aione prefers ./upstreams over empty XDG_DATA_HOME
RUN mkdir -p /app/upstreams \
    && git clone --depth 1 https://github.com/cv-cat/Spider_XHS.git /app/upstreams/Spider_XHS \
    && if [ -f /app/upstreams/Spider_XHS/package.json ]; then npm --prefix /app/upstreams/Spider_XHS install --omit=dev; fi

ENV PYTHONUNBUFFERED=1 \
    XDG_CONFIG_HOME=/data/xhs \
    AIONE_UPSTREAM_ROOT=/app/upstreams

EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
