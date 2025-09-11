#!/usr/bin/env bash
set -euo pipefail
export MODEL_S3_URI="${MODEL_S3_URI:-}"
export MODEL_LOCAL_PATH="${MODEL_LOCAL_PATH:-/models/doctorvit-7b/v1}"
export REDIS_URL="${REDIS_URL:-redis://doctorvit-redis:6379/0}"
if [[ -n "${MODEL_S3_URI}" ]]; then /app/bootstrap_model.sh "${MODEL_S3_URI}" "${MODEL_LOCAL_PATH}"; fi
exec python3 -u /app/worker/worker.py
