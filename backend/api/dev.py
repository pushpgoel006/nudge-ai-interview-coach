"""Run the API for local development on THROWAWAY data. Never touches your real database or vectors.

    .venv\\Scripts\\python -m api.dev

`DATABASE_URL` in .env points at your real (Neon) database, and the vector store and uploads live
inside the project folder. This launcher swaps all three for a temporary folder before the app is
imported, for this process only. It is development tooling: no existing backend file is edited, and
nothing here is used in production (the Docker image starts `api.main:app` directly).

Your Groq key from .env is still used, so chat, resume, theory and DSA make real (small) LLM calls.
"""

import os
import tempfile
from pathlib import Path

# python-dotenv looks for .env from the working folder when started with `python -c` or `-m` from elsewhere,
# so always run from the project root.
os.chdir(Path(__file__).resolve().parent.parent)

DATA = Path(os.getenv("NUDGE_DEV_DATA", Path(tempfile.gettempdir()) / "nudge_dev_data"))
DATA.mkdir(parents=True, exist_ok=True)

# Must be set before `database.db` is imported anywhere. Assigned, never setdefault, so a real URL can't win.
os.environ["DATABASE_URL"] = "sqlite:///" + (DATA / "dev.db").as_posix()
os.environ.pop("DATABASE_URL_UNPOOLED", None)
os.environ.setdefault("API_ENV", "development")
# Generous limits so you can click around without hitting the production quotas.
os.environ.setdefault("API_AI_PER_MINUTE", "200")
os.environ.setdefault("API_AI_PER_DAY", "500")

import rag.retriever as _retriever  # noqa: E402
import rag.vector_store as _vector_store  # noqa: E402

_retriever.CHROMA_DIR = DATA / "chroma"
_vector_store.CHROMA_DIR = DATA / "chroma"

import api.routes.documents as _documents  # noqa: E402

_documents.UPLOADS_DIR = DATA / "uploads"

import uvicorn  # noqa: E402

from api.main import app  # noqa: E402

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Nudge dev API on http://127.0.0.1:{port}  (throwaway data in {DATA})")
    uvicorn.run(app, host="127.0.0.1", port=port)
