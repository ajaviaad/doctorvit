#!/usr/bin/env bash
set -euo pipefail

# Load .env if present
if [[ -f ".env" ]]; then
  set -a; source .env; set +a
fi

: "${MODEL_S3_URI:?MODEL_S3_URI not set}"
: "${MODEL_LOCAL_PATH:?MODEL_LOCAL_PATH not set}"

echo "[BOOTSTRAP] Syncing ${MODEL_S3_URI} -> ${MODEL_LOCAL_PATH}"
mkdir -p "${MODEL_LOCAL_PATH}"
aws s3 sync "${MODEL_S3_URI}" "${MODEL_LOCAL_PATH}" --no-progress
echo "[BOOTSTRAP] Listing files:"
ls -lah "${MODEL_LOCAL_PATH}" || true
echo "[BOOTSTRAP] Done"
