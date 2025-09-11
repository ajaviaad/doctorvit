#!/usr/bin/env bash
set -euo pipefail
_term(){ echo "[SHUTDOWN] SIGTERM - draining 25s"; sleep 25; exit 0; } ; trap _term SIGTERM

export HF_HOME="${HF_HOME:-/models/.cache}"
export VLLM_PORT="${VLLM_PORT:-8000}"
export MAX_MODEL_LEN="${MAX_MODEL_LEN:-2048}"
export MAX_NUM_SEQS="${MAX_NUM_SEQS:-64}"
export MAX_BATCHED_TOKENS="${MAX_BATCHED_TOKENS:-4096}"
export DTYPE="${DTYPE:-bfloat16}"
export TRUST_REMOTE_CODE="${TRUST_REMOTE_CODE:-true}"
export MODEL_S3_URI="${MODEL_S3_URI:-}"
export MODEL_LOCAL_PATH="${MODEL_LOCAL_PATH:-/models/doctorvit-7b/v1}"
[[ -z "${MODEL_S3_URI}" ]] && { echo "[FATAL] MODEL_S3_URI not set"; exit 1; }

/app/bootstrap_model.sh "${MODEL_S3_URI}" "${MODEL_LOCAL_PATH}"

python3 -m vllm.entrypoints.openai.api_server \
  --model "${MODEL_LOCAL_PATH}" \
  --dtype "${DTYPE}" \
  --max-model-len "${MAX_MODEL_LEN}" \
  --max-num-seqs "${MAX_NUM_SEQS}" \
  --max-num-batched-tokens "${MAX_BATCHED_TOKENS}" \
  --trust-remote-code \
  --enforce-eager \
  --host 0.0.0.0 \
  --port "${VLLM_PORT}" &

# Minimal health proxy (optional)
python3 - <<'PY' &
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests, os
PORT=int(os.environ.get("VLLM_PORT","8000"))
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/health"):
            try:
                r = requests.get(f"http://127.0.0.1:{PORT}/health", timeout=2)
                self.send_response(200 if r.ok else 503)
            except Exception:
                self.send_response(503)
            self.send_header("Content-Type","application/json")
            self.end_headers(); self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404); self.end_headers()
HTTPServer(("0.0.0.0", 8081), H).serve_forever()
PY

wait -n
