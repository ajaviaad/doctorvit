# DoctorVIT — Notebook‑Native Deployment (Hyperstack H200)

**Goal:** Run your **exact notebook code** (no external APIs) on a Hyperstack **NVIDIA H200** box.  
The only change you make inside the notebook: **the path to local model files** (weights/tokenizer/transformers). Everything else stays the same.

---

## 0) What you get
- **No OpenAI / no external LLM APIs** — pure local inference.
- **Jupyter Lab** on your H200 machine so you run the **same notebook**.
- Scripts to **sync your model from S3** to a local path (NVMe) and keep it hot in VRAM.
- A minimal **conda + pip** environment with **PyTorch 2.3 (CUDA 12.1)** and **Transformers** pinned for stability.

---

## 1) Provision an H200 VM on Hyperstack
- Ubuntu 22.04, latest NVIDIA driver (Hyperstack images usually include this).
- NVMe SSD recommended for fast local model cache (e.g., `/opt/models`).

---

## 2) Copy this package to the H200 box
```bash
scp -r doctorvit-notebook-native <user>@<h200-host>:/home/<user>/
```

---

## 3) Configure environment variables
Edit **`.env`** (created from `.env.example`) with your S3 path and credentials:

```bash
cp .env.example .env
vim .env
```

- `MODEL_S3_URI`  e.g., `s3://doctorvit/models/doctorvit-7b/v1`
- `MODEL_LOCAL_PATH` default `/opt/models/doctorvit-7b/v1`
- Prefer **instance role / secret manager** over static keys in production.

---

## 4) Create the Python env (no code changes in your notebook)
```bash
sudo bash scripts/setup_conda_env.sh
# this installs Miniforge (conda) if missing, creates env "doctorvit",
# installs PyTorch 2.3 (CUDA 12.1), Transformers, and tools.
```

> Optional speed-ups (can do later): `pip install flash-attn --no-build-isolation` (verify with your custom activation).

---

## 5) Sync your private model from S3 to local NVMe
```bash
source ~/.bashrc
conda activate doctorvit
sudo mkdir -p /opt/models
sudo chown $USER:$USER /opt/models
./scripts/bootstrap_model.sh   # reads .env and performs the sync
ls -lah /opt/models/doctorvit-7b/v1
```

You should see `config.json`, `tokenizer.json`, and `*.safetensors` shards.

---

## 6) Start Jupyter Lab (local, no API changes)
```bash
./jupyter/start_jupyter.sh
# or: jupyter lab --ip 0.0.0.0 --no-browser --NotebookApp.token=''
```

Open `http://<h200-host>:8888` in your browser.  
*(Set a password/token for Internet-facing hosts.)*

---

## 7) Open YOUR existing notebook and change only the model path
Inside your notebook, change **only** the location of the model; keep everything else identical.

```python
MODEL_PATH = "/opt/models/doctorvit-7b/v1"  # <- local path
from transformers import AutoTokenizer, AutoModelForCausalLM

tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, torch_dtype="auto", trust_remote_code=True, device_map="auto"
).eval()
```

> If your notebook already sets dtype/BF16 and imports your custom activation, **leave it as-is**.

Run your usual cells: tokenization, `.generate(...)`, DuckDuckGo integration — **unchanged**.

---

## 8) Tips for stability & speed (optional)
- Keep **context ~2k** and **max_new_tokens ~180–220** (fits your 150–200 words).
- If you see OOM, lower batch size in your code or reduce concurrent notebook users.
- To squeeze more speed later: try **flash-attn**, `torch.set_float32_matmul_precision("high")`, or `torch.compile` if your activation supports it.

---

## 9) Troubleshooting
- **Module import errors**: ensure your custom activation code lives next to `config.json` or is pip-installable; use `trust_remote_code=True`.
- **Slow first run**: that’s weight load + warm-up; subsequent runs are fast.
- **S3 auth**: test with `aws s3 ls $MODEL_S3_URI`; set a VPC endpoint or private route if applicable.

---

## 10) Security
- Never commit model files or secrets to Git. Use private buckets and restricted IAM.
- If you expose Jupyter publicly, **set a strong token/password**.

---

**That’s it.** Your notebook stays **100% the same** except for the single `MODEL_PATH` line above.
