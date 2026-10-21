# Nudge API on a Hugging Face Space (Docker). CPU only.
# Copy this file to the ROOT of the Space repo, next to the backend code (see deploy/README.md).
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/user/.cache/huggingface \
    API_ENV=production

# Hugging Face runs Spaces as user 1000.
RUN useradd -m -u 1000 user
WORKDIR /app

# System libs PyMuPDF and the ML stack need at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY --chown=user requirements.txt /app/requirements.txt

# requirements.txt is a full lock for Windows development. Drop the Linux CUDA wheels (several GB
# on a CPU-only Space) and install CPU PyTorch instead; everything else is installed as locked.
RUN grep -v -i -E '^(nvidia-|cuda-|triton|torch==)' requirements.txt > requirements.space.txt \
    && pip install torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.space.txt

COPY --chown=user . /app
USER user

# Fetch the embedding model at build time so the first request is not a cold download.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

EXPOSE 7860
COPY --chown=user deploy/huggingface/start.sh /app/start.sh
CMD ["bash", "/app/start.sh"]
