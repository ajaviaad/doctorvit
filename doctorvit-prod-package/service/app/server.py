# app/server.py
from fastapi import FastAPI
from pydantic import BaseModel
from .loader import generate_text

app = FastAPI(title="DoctorVIT Transformers-native Service", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

class Req(BaseModel):
    prompt: str
    max_new_tokens: int = 200
    temperature: float = 0.2
    top_p: float = 1.0
    do_sample: bool = False

@app.post("/generate")
def generate(req: Req):
    text = generate_text(req.prompt, req.max_new_tokens, req.temperature, req.top_p, req.do_sample)
    return {"text": text}
