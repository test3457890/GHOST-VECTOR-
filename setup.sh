#!/usr/bin/env bash
# GHOST VECTOR CTF: one-step build and launch
set -e
cd "$(dirname "$0")"
if docker compose version >/dev/null 2>&1; then DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then DC="docker-compose"
else echo "Docker Compose not found. See docs/DEPLOYMENT.md"; exit 1; fi
if [ ! -f config/flags.env ]; then
  cp config/flags.example.env config/flags.env
  echo "Created config/flags.env from the example. Edit it before a real event."
fi
$DC up -d --build
echo "GHOST VECTOR is starting at http://${HOST_BIND_IP:-127.0.0.1}:${HOST_PORT:-8080}"
