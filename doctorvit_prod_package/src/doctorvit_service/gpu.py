
import json, os
import torch

def gpu_info():
    info = {"cuda_available": torch.cuda.is_available()}
    if torch.cuda.is_available():
        i = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(i)
        info.update({
            "device_index": i,
            "name": props.name,
            "total_mem_gb": round(props.total_memory / (1024**3), 2),
            "cc": f"{props.major}.{props.minor}",
        })
    return info

def assert_hopper_or_newer():
    if not torch.cuda.is_available():
        return
    i = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(i)
    # Hopper/H100/H200 are compute capability 9.0 (sm_90)
    cc = props.major + props.minor/10
    if cc < 9.0:
        raise RuntimeError("GPU compute capability must be >= 9.0 (Hopper/H200). Detected: "
                           f"{props.major}.{props.minor}")
