#!/bin/sh
set -e

if [ ! -f gemma3-270m-it-q8.litertlm ]; then
    python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='litert-community/gemma-3-270m-it', filename='gemma3-270m-it-q8.litertlm', local_dir='.')"
fi

exec python server.py
