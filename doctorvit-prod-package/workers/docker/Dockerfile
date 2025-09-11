# Transformers-native queue worker (no HTTP)
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip git curl ca-certificates jq tini && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip &&     python3 -m pip install --no-cache-dir torch==2.3.* --index-url https://download.pytorch.org/whl/cu121 &&     python3 -m pip install --no-cache-dir transformers>=4.43,<4.46 accelerate>=0.30,<0.35 safetensors>=0.4 redis>=5 rq==1.16.* awscli
WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
COPY bootstrap_model.sh /app/bootstrap_model.sh
COPY worker /app/worker
RUN chmod +x /app/entrypoint.sh /app/bootstrap_model.sh
ENTRYPOINT ["/usr/bin/tini","--","/app/entrypoint.sh"]
