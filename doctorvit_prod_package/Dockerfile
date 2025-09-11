
# CUDA 12.1 + cuDNN 9 runtime with PyTorch 2.4.x
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

# Ensures reproducible noninteractive installs
ENV DEBIAN_FRONTEND=noninteractive             PYTHONDONTWRITEBYTECODE=1             PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates tini build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -ms /bin/bash appuser
WORKDIR /app

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install PyTorch pinned to CUDA 12.1 wheels (Hopper/H200 compatible)
RUN pip install --index-url https://download.pytorch.org/whl/cu121 torch==2.4.1 torchvision==0.19.1

# Copy code
COPY src /app/src
COPY app /app/app
COPY notebooks /app/notebooks
COPY scripts /app/scripts
COPY pyproject.toml README.md /app/

ENV PYTHONPATH=/app/src:$PYTHONPATH

# Runtime envs
ENV WORKERS=1 \
    PORT=8000 \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Health check path
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:${PORT}/healthz || exit 1

EXPOSE 8000

# Use tini as PID 1 for signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-keep-alive", "10", "--limit-concurrency", "1000"]
