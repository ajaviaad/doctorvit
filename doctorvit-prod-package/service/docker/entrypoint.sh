#!/usr/bin/env bash
set -euo pipefail
_term(){ echo "[SHUTDOWN] SIGTERM - draining 15s"; sleep 15; exit 0; } ; trap _term SIGTERM
export HF_HOME="${HF_HOME:-/models/.cache}"
export MODEL_S3_URI="${MODEL_S3_URI:-}"
export MODEL_LOCAL_PATH="${MODEL_LOCAL_PATH:-/models/doctorvit-7b/v1}"
export SERVER_PORT="${SERVER_PORT:-8000}"
if [[ -n "${MODEL_S3_URI}" ]]; then /app/bootstrap_model.sh "${MODEL_S3_URI}" "${MODEL_LOCAL_PATH}"; fi
exec uvicorn app.server:app --host 0.0.0.0 --port "${SERVER_PORT}" --timeout-keep-alive 120
