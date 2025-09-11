
import os, uuid, time
import papermill as pm
from .settings import settings

def run_notebook(parameters: dict | None = None) -> dict:
    os.makedirs(settings.artifacts_dir, exist_ok=True)
    run_id = str(uuid.uuid4())
    out_ipynb = os.path.join(settings.artifacts_dir, f"run_{run_id}.ipynb")
    # Execute the notebook as-is.
    pm.execute_notebook(
        settings.notebook_path,
        out_ipynb,
        parameters=parameters or {},
        cwd=os.path.dirname(settings.notebook_path) or "."
    )
    return {"run_id": run_id, "executed_notebook": out_ipynb}
