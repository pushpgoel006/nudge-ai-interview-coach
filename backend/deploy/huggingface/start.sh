#!/usr/bin/env bash
# Container entry point for the Hugging Face Space.
set -euo pipefail

# If persistent storage is attached to the Space (it is mounted at /data), keep the Chroma vector
# store there so indexed documents survive restarts. The backend code is unchanged: it still reads
# ./chroma_db, which here is a link to the persistent folder. Without persistent storage the free
# disk is wiped on every restart; the API then flags affected documents as "needs re-adding".
if [ -d /data ] && [ -w /data ]; then
  mkdir -p /data/chroma_db
  rm -rf /app/chroma_db
  ln -s /data/chroma_db /app/chroma_db
fi

exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-7860}" --proxy-headers --forwarded-allow-ips="*"
