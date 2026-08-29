#!/bin/sh
set -eu
curl -fsS "http://127.0.0.1:${APP_PORT:-8000}/health"
echo
curl -fsS "http://127.0.0.1:${APP_PORT:-8000}/" >/dev/null
echo frontend_ok
