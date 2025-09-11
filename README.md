# DoctorVIT – Production Ready Package

DoctorVIT is a production-ready scaffold for serving notebook-based ML inference via FastAPI with background processing through Celery + Redis. It runs locally with Docker Compose and deploys to Kubernetes with GPU workers, autoscaling, health checks, and metrics.

---

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
  - [Local (Docker Compose)](#local-docker-compose)
  - [Kubernetes (Helm)](#kubernetes-helm)
- [API](#api)
- [Scaling & Autoscaling](#scaling--autoscaling)
- [Health, Readiness & Metrics](#health-readiness--metrics)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Helm Values](#helm-values)
- [GPU & Model Warmup](#gpu--model-warmup)
- [Observability & Logging](#observability--logging)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [License](#license)

---

## Architecture

```
Client → FastAPI (HTTP)
             │
             ├── /predict → Enqueue Celery task
             └── /run-notebook → Execute notebook via Papermill

Redis (broker/result) ←→ Celery Worker(s) (1 GPU per worker)
```

- **API**: FastAPI app (`/predict`, `/run-notebook`, `/healthz`, `/metrics`)
- **Workers**: Celery worker(s) consuming queue `gpu`
- **Notebook**: Executed unchanged via Papermill; converted to a module for function calls
- **GPU**: Each worker reserves a GPU; scale workers horizontally

---

## Features

- Serve notebook inference **without modifying prompts or model code**
- Background execution using Celery (GPU-aware)
- Dockerized builds with pinned dependencies
- Kubernetes Helm chart with:
  - API + Worker + Redis deployments
  - **Liveness/Readiness** probes
  - **Horizontal Pod Autoscalers (HPA)** for API and Worker
  - Optional **PodDisruptionBudgets (PDB)**
- Prometheus metrics at `/metrics`

---

## Quick Start

### Local (Docker Compose)

Prereqs: NVIDIA driver + `nvidia-container-toolkit` for GPU, Docker 24+

```bash
docker compose up --build -d
curl localhost:8000/healthz
curl -X POST localhost:8000/predict -H 'content-type: application/json'   -d '{"data":{"text":"hello world"}}'
curl -X POST localhost:8000/run-notebook -H 'content-type: application/json' -d '{}'
```

### Kubernetes (Helm)

Prereqs:
- Kubernetes ≥ 1.23 (HPA v2)
- NVIDIA Device Plugin installed on nodes with GPUs
- A container registry containing your API/Worker images

1. Push images or set your registry in `values.yaml`:

```yaml
image:
  repository: <your-registry>/doctorvit-api
  tag: <version-or-git-sha>
worker:
  repository: <your-registry>/doctorvit-worker
  tag: <version-or-git-sha>
```

2. Install/upgrade the chart:

```bash
helm upgrade --install doctorvit ./infra/helm
kubectl get pods
kubectl port-forward deploy/doctorvit-api 8000:8000
curl localhost:8000/healthz
```

---

## API

- `GET /healthz` – health/readiness endpoint used by probes
- `GET /metrics` – Prometheus metrics
- `POST /predict` – enqueue inference using your notebook's exported `predict(payload)`
- `GET /predict/{task_id}` – check task status/result
- `POST /run-notebook` – execute the notebook as-is (Papermill)
- `GET /run-notebook/{task_id}` – check notebook run status/result

**NOTE:** The notebook must expose `def predict(payload): ...` or a callable `pipe/pipeline`. This repository includes a minimal adapter cell that preserves your exact prompts and model logic.

---

## Scaling & Autoscaling

- **API HPA**: CPU+Memory-based (default 70% CPU / 80% Memory)
- **Worker HPA**: CPU-based by default (70%), typically 1 GPU per worker

Edit `values.yaml`:

```yaml
hpa:
  api:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 70
      - type: Resource
        resource:
          name: memory
          target:
            type: Utilization
            averageUtilization: 80
  worker:
    enabled: true
    minReplicas: 1
    maxReplicas: 8
    metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 70
```

> Advanced: For queue-length scaling, integrate KEDA and use Redis queue depth as a metric for Worker autoscaling.

---

## Health, Readiness & Metrics

**API Probes** (HTTP):
- `livenessProbe` → `GET /healthz`
- `readinessProbe` → `GET /healthz`

**Worker Probes** (Exec):
- Executes a short Python script to `PING` Redis (ensures the worker can accept jobs).

Defaults are defined in `values.yaml` under `probes.*`.

**Metrics**:
- `/metrics` (Prometheus format) exposed by the API. Scrape with your Prometheus Operator or sidecar.

---

## Configuration

### Environment Variables

| Variable          | Component | Default           | Description                                  |
|-------------------|-----------|-------------------|----------------------------------------------|
| `REDIS_HOST`      | API/Worker| `doctorvit-redis` | Redis service host                           |
| `REDIS_PORT`      | API/Worker| `6379`            | Redis service port                           |
| `REQUIRE_HOPPER`  | Worker    | `0`               | If `1`, enforce Hopper GPUs only             |

### Helm Values

Key sections:
- `image`, `worker` – image repository/tags
- `resources` – CPU/Memory and `nvidia.com/gpu` requests/limits
- `probes` – liveness/readiness configuration
- `hpa` – HorizontalPodAutoscaler settings
- `pdb` – PodDisruptionBudget toggles

---

## GPU & Model Warmup

- Each Celery worker should request **`nvidia.com/gpu: 1`**.
- Add model warmup in FastAPI `@app.on_event("startup")` to reduce first-request latency.
- Pre-download models at container start to avoid on-request downloads.

---

## Observability & Logging

- Structured logs (JSON) recommended for API and worker.
- Trace request IDs through API → task.
- Expose `/metrics` and configure scraping via ServiceMonitor (if using Prometheus Operator).

---

## Security

- Avoid embedding tokens in notebooks; use Kubernetes Secrets or build-time secrets.
- Consider running containers as non-root (`securityContext`) and read-only root FS.
- Restrict network policies (allow API ↔ Redis, Worker ↔ Redis).

---

## Troubleshooting

- **API CrashLoopBackOff**: Check `kubectl logs deploy/doctorvit-api`. Ensure `/healthz` returns 200 and models load.
- **Worker Not Ready**: Probe may fail if `redis` Python pkg missing; ensure it’s installed. Verify `REDIS_HOST`.
- **HPA Not Scaling**: Confirm Metrics Server is installed and `kubectl top pods` works.
- **GPU Scheduling**: Verify NVIDIA device plugin and that nodes advertise `nvidia.com/gpu`.

---

## FAQ

**Q: Do I have to change my notebook prompts?**  
A: No. The adapter exports a `predict(payload)` function that calls your existing pipeline unchanged.

**Q: Can I scale workers by queue depth?**  
A: Yes—use KEDA with Redis Scaler. This chart ships CPU-based HPA by default.

---

## License

© 2025 DoctorVIT. Proprietary and confidential. All rights reserved.
