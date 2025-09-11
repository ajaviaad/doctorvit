
import os, subprocess, sys, shutil
from .settings import settings

def convert_notebook_to_py(notebook_path: str, out_py: str) -> str:
    os.makedirs(os.path.dirname(out_py), exist_ok=True)
    # Use nbconvert to export to Python
    cmd = [sys.executable, "-m", "jupyter", "nbconvert", "--to", "script", notebook_path, "--output", "converted_module"]
    subprocess.check_call(cmd, cwd=os.path.dirname(out_py))
    # nbconvert will drop into the cwd with name converted_module.py
    return out_py
