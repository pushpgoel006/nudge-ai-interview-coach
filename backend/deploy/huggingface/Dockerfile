# Nudge API in a Docker container (Render, Hugging Face Spaces, Cloud Run, ...). CPU only.
# Build context is the backend folder (the one that contains api/, rag/, deploy/).
FROM python:3.14-slim

# Embeddings run through ONNX Runtime (same all-MiniLM-L6-v2 model), so PyTorch is not installed.
# That keeps the API near 250 MB of memory instead of about 500 MB. See rag/embeddings.py.
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    API_ENV=production \
    EMBEDDINGS_BACKEND=onnx \
    MALLOC_ARENA_MAX=2 \
    TOKENIZERS_PARALLELISM=false

# Hosts run the container as a non-root user (Hugging Face uses uid 1000).
RUN useradd -m -u 1000 user
WORKDIR /app

COPY --chown=user requirements.txt /app/requirements.txt

# requirements.txt is a full lock made on Windows. Leave out the PyTorch stack (torch, its CUDA wheels,
# transformers, sentence-transformers and the LangChain wrapper around them): the ONNX path does not
# use them, and they are several GB. Everything else is installed as locked.
RUN grep -v -i -E '^(nvidia-|cuda-|triton|torch==|transformers==|sentence-transformers==|langchain-huggingface==)' requirements.txt > requirements.space.txt \
    && pip install -r requirements.space.txt

COPY --chown=user . /app
# /app itself is created by root (WORKDIR), so the app user could not create ./uploads or ./chroma_db.
RUN mkdir -p /app/uploads /app/chroma_db && chown user:user /app /app/uploads /app/chroma_db
USER user

# Fetch the embedding model at build time so the first request is not a cold download.
RUN python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()(['warm up'])"

EXPOSE 7860
COPY --chown=user deploy/huggingface/start.sh /app/start.sh
CMD ["bash", "/app/start.sh"]
