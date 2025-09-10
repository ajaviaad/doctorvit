#!/usr/bin/env bash
set -euo pipefail

# Install Miniforge (conda) if missing
if ! command -v conda >/dev/null 2>&1; then
  echo "[SETUP] Installing Miniforge..."
  curl -L -o /tmp/miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
  bash /tmp/miniforge.sh -b -p $HOME/miniforge3
  eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
  conda init bash
else
  echo "[SETUP] Conda already installed."
  eval "$(conda shell.bash hook)"
fi

echo "[SETUP] Creating conda env 'doctorvit' (Python 3.10)"
conda create -y -n doctorvit python=3.10
conda activate doctorvit

echo "[SETUP] Installing PyTorch 2.3 (CUDA 12.1) and deps"
pip install --upgrade pip
pip install "torch==2.3.*" --index-url https://download.pytorch.org/whl/cu121
pip install "transformers>=4.43,<4.46" "accelerate>=0.30,<0.35" "safetensors>=0.4" "tokenizers>=0.15,<0.20" "sentencepiece>=0.1.99" "numpy>=1.26" "pydantic<3" "requests" "awscli"
# Optional performance packages (uncomment once your activation is validated with them)
# pip install flash-attn --no-build-isolation

echo "[SETUP] Done. Activate with:  conda activate doctorvit"
