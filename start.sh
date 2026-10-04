#!/bin/sh
set -e

PYTHON="/workspace/.deployhatch-venv/bin/python"

echo "Using: $PYTHON"
"$PYTHON" -c "import huggingface_hub; print('huggingface_hub OK')"

if [ ! -f gemma3-270m-it-q8.litertlm ]; then
    "$PYTHON" -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='litert-community/gemma-3-270m-it', filename='gemma3-270m-it-q8.litertlm', local_dir='.')"
fi

exec "$PYTHON" server.py
