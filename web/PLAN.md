# Nudge: build plan

Portfolio site for the AI interview coach. Frontend: Next.js on Vercel. Backend: the existing
Python project (LangChain + LangGraph) behind a new FastAPI layer, hosted on Hugging Face Spaces.

## Ground rules

- **The AI backend is not modified.** Everything under `agents/`, `graphs/`, `rag/`, `prompts/`,
  `models/`, `services/` and `database/` stays exactly as it is: how documents are loaded, split,
  embedded and retrieved, and how the LangGraph graphs and LLM calls run.
- New backend code lives only in a new `api/` folder (plus its tests). It imports the existing
  graphs and services and exposes them over HTTP. Streamlit keeps working until we retire it.
- One exception, and it needs an explicit OK first: Section 10 may move the vector store off the
  local Chroma folder, because Hugging Face's free disk is wiped on restart.
- The frontend never holds secrets. The Groq key and database URL live only on the backend host.
- Backend location: the `backend/` folder of this repo.

## Sections

Each section is built, checked and reported on its own before the next starts.

| # | Section | Result | Status |
|---|---|---|---|
| 1 | Next.js landing page | Port of the scroll story to Next.js, deployable to Vercel as-is | **Done** |
| 2 | API foundation | `api/` FastAPI app: health, CORS, config, cookie login (register, login, logout, me), sessions CRUD with owner checks, tests | **Done** |
| 3 | Studio shell | `/studio` route: sign-in and sign-up, session list and create, shared layout with one section per tool | **Done** |
| 4 | Documents | Upload PDF, paste text, choose type, index, list, delete; flags documents missing from the vector store | **Done** |
| 5 | Chat | Calls `rag_graph`; answer, sources, retrieval steps (parts, passages kept, retries) | **Done** |
| 6 | Resume check | Calls `resume_graph`; fit score, verdicts, suggestions, last saved review | **Done** |
| 7 | Theory round | New question, answer, evaluation, up to 3 follow-ups via `interview_graph`; state held server-side | **Done** |
| 8 | DSA round | Problem fetch, code submit, judged review via `dsa_graph`; state held server-side | **Done** |
| 9 | Dashboard | Readiness, theory trend, topic scores, weakest topics, recommendations | **Done** |
| 10 | Guardrails | Per-account and site-wide AI quotas, throttling, size caps, delete-my-data, optional auto-expiry. Vector-store move NOT done (needs your OK) | **Done** (minus vector store) |
| 11 | Deploy | Dockerfile + start script for Hugging Face Spaces, deploy guide, env docs, `BACKEND_URL` rewrite for Vercel, live smoke test | **Done** (not yet deployed) |

## Studio structure (reworked after Section 11)

- `/studio`: choose or create a prep session. Creating one goes to `/studio/documents` (step 1: add documents, step 2: pick what to practise).
- Top-bar navigation: Documents, Chat, Resume check, Theory round, DSA round, Dashboard. Guided, never blocked: pages show a gentle
  "add documents" note when the session has none.
- Dashboard: readiness donut (60% theory / 40% resume split), score trend line with Theory/DSA toggles, and topic strength as
  bars or radar. Click a topic to practise it or get advice.

## Notes

- The Streamlit UI calls these entry points directly; the API will call the same ones:
  `rag_graph.invoke`, `resume_graph.invoke`, `generate_grounded_question`, `interview_graph.invoke`,
  `dsa_graph.invoke`, `generate_recommendation`, and the `services.*` and `services.analytics` helpers.
- The graphs return in one piece (no token streaming), so the UI shows the retrieval steps and
  progress states instead of streaming text.
- Local dev: `npm run dev:all` starts the site and the API together (API on throwaway data); or run `python -m api.dev` and `npm run dev` separately; Next.js on port 3000 proxies `/api/*` to port 8000.
- The "Launch app" button reads `NEXT_PUBLIC_APP_URL`; once `/studio` exists it points there.

## Safety rule learned the hard way

Never run backend code or tests against the real database. The backend's `.env` points `DATABASE_URL` at the real
Neon database, and `database.db` reads it at import time. Use `python -m api.dev` for local runs. The `tests_api`
package forces a throwaway SQLite database before anything is imported and refuses to run otherwise.
