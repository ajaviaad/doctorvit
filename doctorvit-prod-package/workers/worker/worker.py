# worker/worker.py
import os, sys, time, json
import redis
from rq import Queue, Worker, Connection
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

REDIS_URL = os.environ.get("REDIS_URL","redis://doctorvit-redis:6379/0")
QUEUE_NAME = os.environ.get("QUEUE_NAME","doctorvit:queue")
MODEL_LOCAL_PATH = os.environ.get("MODEL_LOCAL_PATH","/models/doctorvit-7b/v1")
TRUST_REMOTE_CODE = os.environ.get("TRUST_REMOTE_CODE","true").lower()=="true"

if MODEL_LOCAL_PATH not in sys.path:
    sys.path.insert(0, MODEL_LOCAL_PATH)

print(f"[BOOT] Loading model from {MODEL_LOCAL_PATH}")
tok = AutoTokenizer.from_pretrained(MODEL_LOCAL_PATH, trust_remote_code=TRUST_REMOTE_CODE)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_LOCAL_PATH, torch_dtype=torch.bfloat16, trust_remote_code=TRUST_REMOTE_CODE, device_map="auto"
).eval()

def infer(prompt, max_new_tokens=200, temperature=0.2, top_p=1.0, do_sample=False):
    ids = tok(prompt, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        out = model.generate(**ids, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, do_sample=do_sample)
    return tok.decode(out[0], skip_special_tokens=True)

def job_runner(payload: dict):
    return infer(
        payload.get("prompt",""),
        max_new_tokens=int(payload.get("max_new_tokens",200)),
        temperature=float(payload.get("temperature",0.2)),
        top_p=float(payload.get("top_p",1.0)),
        do_sample=bool(payload.get("do_sample",False)),
    )

if __name__ == "__main__":
    conn = redis.from_url(REDIS_URL)
    with Connection(conn):
        q = Queue(QUEUE_NAME)
        # Register function name for enqueuer
        import rq
        from rq import Worker
        # Worker will import this module and resolve job_runner by name
        worker = Worker([q])
        print(f"[READY] Worker listening on {QUEUE_NAME} via {REDIS_URL}")
        worker.work(with_scheduler=True)
