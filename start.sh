#!/bin/sh
set -e

PYTHON="/workspace/.deployhatch-venv/bin/python"

echo "Using: $PYTHON"

"$PYTHON" -c "import huggingface_hub; print('huggingface_hub OK')"

if [ ! -f SmolLM2_135M_Instruct.litertlm ]; then
    echo "Downloading SmolLM2-135M-Instruct..."
    "$PYTHON" -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='litert-community/SmolLM2-135M-Instruct', filename='SmolLM2_135M_Instruct.litertlm', local_dir='.')"
fi

echo "Starting NEXUS-AI..."
exec "$PYTHON" server.py
