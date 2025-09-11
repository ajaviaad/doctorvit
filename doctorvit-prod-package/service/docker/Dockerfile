# Transformers-native service runtime (no OpenAI semantics)
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip git curl ca-certificates unzip jq tini && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip &&     python3 -m pip install --no-cache-dir torch==2.3.* --index-url https://download.pytorch.org/whl/cu121 &&     python3 -m pip install --no-cache-dir transformers>=4.43,<4.46 accelerate>=0.30,<0.35 safetensors>=0.4 fastapi>=0.110,<0.115 uvicorn>=0.29,<0.31 pydantic<3 awscli
WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
COPY bootstrap_model.sh /app/bootstrap_model.sh
COPY app /app/app
RUN chmod +x /app/entrypoint.sh /app/bootstrap_model.sh
EXPOSE 8000
ENTRYPOINT ["/usr/bin/tini","--","/app/entrypoint.sh"]
