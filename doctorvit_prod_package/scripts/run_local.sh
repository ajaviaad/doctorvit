
#!/usr/bin/env bash
set -euo pipefail
export UVICORN_WORKERS=${UVICORN_WORKERS:-1}
export PORT=${PORT:-8000}
# Start the API locally (CPU). For GPU use Docker.
python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --workers "${UVICORN_WORKERS}"
