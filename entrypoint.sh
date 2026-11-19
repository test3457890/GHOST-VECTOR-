#!/bin/sh
set -e
# Generate challenge data on first boot (or when REGENERATE=1).
if [ ! -f "$OUTPUT_DIR/.hashes.json" ] || [ "$REGENERATE" = "1" ]; then
  python /app/generator.py
fi
exec gunicorn --bind "0.0.0.0:${PORT}" --workers 1 --threads 8 --worker-tmp-dir /tmp \
  --limit-request-line 2048 --limit-request-fields 50 --timeout 30 --access-logfile - app:app
