import importlib.util
import os
import sys

from .celery_app import celery_app
from doctorvit_service.notebook_runner import run_notebook
from doctorvit_service.settings import settings
from doctorvit_service.converter import convert_notebook_to_py


@celery_app.task(name="tasks.run_notebook_task")
def run_notebook_task(params: dict | None = None):
    return run_notebook(params)


def _load_converted_module():
    os.makedirs(os.path.dirname(settings.converted_module_path), exist_ok=True)
    convert_notebook_to_py(settings.notebook_path, settings.converted_module_path)
    spec = importlib.util.spec_from_file_location("converted_module", settings.converted_module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["converted_module"] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@celery_app.task(name="tasks.predict_task")
def predict_task(payload: dict):
    module = _load_converted_module()
    # Prefer explicit predict() if you add it later
    if hasattr(module, "predict"):
        return module.predict(payload)
    # Fallbacks that DO NOT change your prompts/inference:
    # - Call predict_one()/infer()/inference(payload) if present
    for name in ("predict_one", "infer", "inference"):
        if hasattr(module, name):
            return getattr(module, name)(payload)
    # - Or call a HF pipeline object named `pipe` or `pipeline`
    for name in ("pipe", "pipeline"):
        if hasattr(module, name):
            pipe = getattr(module, name)
            data = payload.get("text") or payload.get("inputs") or payload
            return pipe(data)
    raise AttributeError(
        "No predict() in notebook. Add a cell with `def predict(input): ...`, "
        "or expose a callable `pipe`/`pipeline`."
    )
