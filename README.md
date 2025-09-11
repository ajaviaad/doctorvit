# DoctorVIT — Production Bundle

This bundle contains **two production-safe patterns**, both **Transformers-native** using exact jupyter notebook `.generate(...)` code path and custom activation.

Domains & TLS: **doctorvit.eu** with **GoDaddy** certificate (via Kubernetes TLS secret).

## Patterns

### A) Transformers-Native Microservice (HTTP, internal schema)
- Minimal FastAPI app exposes `/health` and `/generate` (simple JSON). Under the hood it calls **`AutoModelForCausalLM.generate`** exactly like jupyter notebook.
- 1 GPU per pod; scale with HPA/KEDA; serves traffic via **Ingress** on `doctorvit.eu`.
- Use when you want a service endpoint for apps/users.

### B) Transformers-Native Queue Workers (no HTTP required)
- **Workers** load the model once and read jobs from **Redis** (RQ). Each job contains your prompt and generation args.
- Scale workers horizontally via **KEDA** on Redis queue length (install KEDA in your cluster). No API semantics exposed.
- Use when you want internal job-based scaling and zero external endpoints.

## TLS (GoDaddy)
- Create a Kubernetes TLS secret `doctorvit-eu-tls` from your GoDaddy cert (see service/README.md).

## S3 Weights
- Both patterns sync your private model repo from **S3 → local NVMe** at pod start, then keep it resident in **VRAM**.

## Directory Layout
- `service/` — Microservice (FastAPI), Docker, K8s (Ingress for doctorvit.eu).
- `workers/` — Redis + RQ workers, K8s (Redis, Worker, optional KEDA ScaledObject), sample enqueuer.
- `shared/k8s/` — Namespace + Secrets template (S3 + optional tokens).

---

**Everything stays Transformers-native.** Your notebook code remains the source of truth; the server and workers call `.generate(...)` in the same way.
