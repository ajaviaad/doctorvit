# DoctorVIT — Transformers-Native Microservice (doctorvit.eu, GoDaddy TLS)

- **No OpenAI** semantics. Minimal JSON over HTTP.
- Calls **Transformers `.generate(...)`** under the hood (your exact path).
- 1 GPU per pod; horizontally scalable; TLS via your **GoDaddy** cert.

## Deploy

1) Build & push:
```bash
docker build -t <registry>/doctorvit-transformers-svc:latest ./docker
docker push <registry>/doctorvit-transformers-svc:latest
```

2) Apply shared base:
```bash
kubectl apply -f ../shared/k8s/namespace.yaml
kubectl apply -f ../shared/k8s/secrets/s3-secrets.yaml
```

3) Create TLS secret from GoDaddy cert (one-time):
```bash
# if you have certificate.crt, gd_bundle.crt, and privkey.pem
cat certificate.crt gd_bundle.crt > fullchain.pem
kubectl -n doctorvit create secret tls doctorvit-eu-tls --cert=fullchain.pem --key=privkey.pem
```

4) Set your image in `k8s/deployment.yaml`, then:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
```

5) DNS: point **doctorvit.eu** (and `www`) to the Ingress external IP.

6) Test:
```bash
curl -s https://doctorvit.eu/health
curl -s https://doctorvit.eu/generate -H "Content-Type: application/json" -d '{"prompt":"Hello DoctorVIT!","max_new_tokens":200}'
```

## Notes
- Generation params map 1:1 to your notebook. Keep `max_new_tokens` ~180–220 for 150–200 words.
- Adjust `DTYPE` (default BF16) via env if you need FP16. Validate FP8 carefully if you try it.
