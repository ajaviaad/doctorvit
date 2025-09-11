# vLLM runtime for DoctorVIT on H200
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python3-dev git curl ca-certificates unzip jq tini \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir "torch==2.3.*" --index-url https://download.pytorch.org/whl/cu121 && \
    python3 -m pip install --no-cache-dir "vllm>=0.5.4,<0.7.0" "transformers>=4.43,<4.46" "accelerate>=0.30,<0.35" \
    "uvicorn>=0.29,<0.31" "fastapi>=0.110,<0.115" "pydantic<3" "awscli" "prometheus-client"
WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
COPY bootstrap_model.sh /app/bootstrap_model.sh
RUN chmod +x /app/entrypoint.sh /app/bootstrap_model.sh
EXPOSE 8000
ENTRYPOINT ["/usr/bin/tini","--","/app/entrypoint.sh"]
