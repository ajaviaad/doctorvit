from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from doctorvit_service.gpu import gpu_info
from .celery_app import celery_app

# Metrics
from starlette_exporter import PrometheusMiddleware, handle_metrics

app = FastAPI(title="DoctorVIT Service", version="0.1.0")
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

class PredictPayload(BaseModel):
    data: dict

class NotebookParams(BaseModel):
    params: dict | None = None

@app.on_event("startup")
def _startup():
    # Lightweight warmup: probe GPU; optional place to preload models
    try:
        _ = gpu_info()
    except Exception:
        pass

@app.get("/healthz")
def healthz():
    return {"ok": True, "gpu": gpu_info()}

@app.post("/predict")
def predict(payload: PredictPayload):
    task = celery_app.send_task("tasks.predict_task", kwargs={"payload": payload.data})
    return {"task_id": task.id}

@app.get("/predict/{task_id}")
def predict_status(task_id: str):
    res = celery_app.AsyncResult(task_id)
    if res.state == "FAILURE":
        raise HTTPException(status_code=500, detail=str(res.info))
    return {"state": res.state, "result": getattr(res, "result", None)}

@app.post("/run-notebook")
def run_notebook(params: NotebookParams):
    task = celery_app.send_task("tasks.run_notebook_task", kwargs={"params": params.params or {}})
    return {"task_id": task.id}

@app.get("/run-notebook/{task_id}")
def run_notebook_status(task_id: str):
    res = celery_app.AsyncResult(task_id)
    if res.state == "FAILURE":
        raise HTTPException(status_code=500, detail=str(res.info))
    return {"state": res.state, "result": getattr(res, "result", None)}
