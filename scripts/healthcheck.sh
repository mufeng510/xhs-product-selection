#!/bin/sh
set -eu
curl -fsS "http://127.0.0.1:${API_PORT:-8000}/health"
echo
curl -fsS "http://127.0.0.1:${WEB_PORT:-3000}/" >/dev/null
echo frontend_ok
