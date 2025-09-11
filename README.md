# DoctorVIT — Hyperstack H200 Production (doctorvit.eu)

This scaffold is pre-configured to expose your service at **https://doctorvit.eu** with Let's Encrypt TLS.

## Quick start

1) **Build & push** your image
```
docker build -t <registry>/doctorvit-vllm-h200:latest ./docker
docker push <registry>/doctorvit-vllm-h200:latest
```

2) **Create namespace, secrets, issuer, deploy**
```
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets/s3-secrets.yaml
kubectl apply -f k8s/cert-manager/cluster-issuer.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/pdb.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
```

3) **DNS**
- After `Service` is created, note the external IP: `kubectl -n doctorvit get svc doctorvit-vllm-svc`.
- Create an **A record** for `doctorvit.eu` (and optional `www.doctorvit.eu`) pointing to that IP.
- Cert-manager will issue a TLS cert automatically (HTTP-01 challenge via Ingress).

4) **Health check**
```
curl -s https://doctorvit.eu/health
```

## Tunables
- Edit `k8s/deployment.yaml`: set your image at `REPLACE_WITH_REGISTRY/doctorvit-vllm-h200:latest`.
- Secret file `k8s/secrets/s3-secrets.yaml`: set `MODEL_S3_URI` and AWS credentials (or switch to workload identity/IRSA).
- HPA is CPU-based by default; for GPU metrics, switch to DCGM exporter + Prometheus Adapter and update `k8s/hpa.yaml`.

## Security notes
- Keep S3 credentials in **Secrets**; prefer IAM roles when available.
- Consider adding **NetworkPolicies** to restrict egress to S3 endpoints only.
- Ingress uses `nginx` class and Let's Encrypt **ClusterIssuer** with email `admin@doctorvit.eu`.

