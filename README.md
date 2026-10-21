# Nudge: AI interview coach

A scroll-driven portfolio site and a live studio for an AI interview coach. Upload a job description and a resume,
then practise with grounded chat, a resume check, theory rounds, DSA rounds and a dashboard.

| Folder | What | Deploys to |
|---|---|---|
| [`web/`](web/) | Next.js site: the landing page and the studio UI (`/studio`) | Vercel |
| [`backend/`](backend/) | Python project: the original LangChain + LangGraph interview coach, plus a FastAPI layer in [`backend/api/`](backend/api/) that exposes it over HTTP | Hugging Face Spaces (Docker) |

```
browser ──> Vercel (Next.js)  ── /api/* rewrite ──>  FastAPI (backend/api)  ──>  LangGraph graphs, RAG, Groq LLM
                                                                              └─> Postgres / SQLite, Chroma vector store
```

## Run it locally

You need Node 20+ and Python 3.11+ (the backend uses `uv` or a plain virtual environment).

```bash
# 1. backend dependencies, once
cd backend
uv sync                      # or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env         # not in the repo: see backend/api/README.md for the variables (GROQ_API_KEY, ...)
cd ..

# 2. site dependencies, once
cd web
npm install

# 3. run both together
npm run dev:all              # site http://localhost:3000, studio http://localhost:3000/studio, API http://127.0.0.1:8000
```

`npm run dev:all` starts the API with `python -m api.dev`, which uses a throwaway SQLite database, vector store and
upload folder, so local runs never touch a real database. The AI features still call Groq with your key.

## Where things are documented

- [`web/README.md`](web/README.md) and [`web/PLAN.md`](web/PLAN.md): the site, its structure and the build plan.
- [`backend/api/README.md`](backend/api/README.md): the HTTP API, auth, quotas and limits.
- [`backend/deploy/README.md`](backend/deploy/README.md): deploying the API to Hugging Face Spaces and the site to Vercel.
- [`backend/README.md`](backend/README.md): the original interview coach this is built on.

## Notes

- The AI code (`agents/`, `graphs/`, `rag/`, `prompts/`, `services/`) is the original project's, with prompt and
  retrieval improvements. The `api/` folder, `tests_api/` and `deploy/` are additions.
- No secrets are committed. `.env` files are ignored; set `GROQ_API_KEY`, `DATABASE_URL` and `API_SECRET_KEY`
  on the hosts.
- The Streamlit UI (`backend/app.py`, `backend/ui/`) still works and is kept for reference.
