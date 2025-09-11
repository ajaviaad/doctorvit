#!/usr/bin/env bash
set -euo pipefail
SRC="${1:-}"; DST="${2:-}"
[[ -z "${SRC}" || -z "${DST}" ]] && { echo "Usage: bootstrap_model.sh s3://bucket/path /models/doctorvit-7b/v1"; exit 1; }
mkdir -p "${DST}"
aws s3 sync "${SRC}" "${DST}" --no-progress
ls -lah "${DST}" || true
