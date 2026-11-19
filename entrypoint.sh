#!/bin/sh
set -e
# Generate challenge data on first boot (or when REGENERATE=1).
if [ ! -f "$OUTPUT_DIR/.hashes.json" ] || [ "$REGENERATE" = "1" ]; then
  python /app/generator.py
fi
exec gunicorn --bind "0.0.0.0:${PORT}" --workers 2 --preload app:app
