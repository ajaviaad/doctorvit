# app/loader.py
import os, sys, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_LOCAL_PATH = os.environ.get("MODEL_LOCAL_PATH", "/models/doctorvit-7b/v1")
DTYPE = os.environ.get("DTYPE", "bfloat16").lower()
TRUST_REMOTE_CODE = os.environ.get("TRUST_REMOTE_CODE", "true").lower() == "true"

if MODEL_LOCAL_PATH not in sys.path:
    sys.path.insert(0, MODEL_LOCAL_PATH)

torch_dtype = torch.bfloat16 if DTYPE in ("bf16","bfloat16") else torch.float16
tokenizer = AutoTokenizer.from_pretrained(MODEL_LOCAL_PATH, trust_remote_code=TRUST_REMOTE_CODE)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_LOCAL_PATH,
    torch_dtype=torch_dtype,
    trust_remote_code=TRUST_REMOTE_CODE,
    device_map="auto"
).eval()

def generate_text(prompt: str, max_new_tokens=200, temperature=0.2, top_p=1.0, do_sample=False):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, do_sample=do_sample)
    return tokenizer.decode(out[0], skip_special_tokens=True)
