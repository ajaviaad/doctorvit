#!/usr/bin/env bash
set -euo pipefail
source ~/.bashrc || true
if command -v conda >/dev/null 2>&1; then
  eval "$(conda shell.bash hook)"
  conda activate doctorvit
fi
# NOTE: consider setting a token for security if exposing publicly
jupyter lab --ip 0.0.0.0 --no-browser --NotebookApp.token=''
