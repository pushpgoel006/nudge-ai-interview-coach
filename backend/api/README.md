# Nudge API

A thin HTTP layer over the existing services and LangGraph graphs. It adds files only: nothing
in `agents/`, `graphs/`, `rag/`, `prompts/`, `models/`, `services/` or `database/` is changed.

## Run locally (on throwaway data)

`DATABASE_URL` in `.env` is your real Neon database, and the vector store and uploads live inside the project.
`api.dev` swaps all three for a temporary folder for that process only, so you can sign up, upload and click
around without touching real data:

```powershell
.venv\Scripts\python -m api.dev
```

Your Groq key is still used, so chat, resume, theory and DSA make real (small) LLM calls. To run the plain app
instead (real database!): `python -m uvicorn api.main:app --port 8000`.

Docs (development only): http://127.0.0.1:8000/api/docs

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `API_ENV` | `development` | `production` requires a secret key, turns on secure cookies, hides docs |
| `API_SECRET_KEY` | none | Signs the login cookie. **Required in production.** Without it (dev only) a temporary key is used and logins reset on restart |
| `API_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated site origins allowed to call the API. In production set it to the Vercel URL |
| `API_COOKIE_SECURE` | `true` in production | Send the cookie over HTTPS only |
| `API_COOKIE_SAMESITE` | `lax` | `lax`, `strict` or `none` |
| `API_COOKIE_NAME` | `nudge_session` | Cookie name |
| `API_SESSION_TTL_DAYS` | `7` | How long a login lasts |
| `API_DOCS` | on in development | Serve `/api/docs` |

`DATABASE_URL` is read by the existing `database/db.py`, exactly as the Streamlit app does.

## Endpoints

All under `/api`. Everything except health, register and login needs the login cookie; routes under
`/sessions/{id}` return 404 for a session that is not yours.

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | `?deep=true` also checks the database |
| POST | `/auth/register` | Create account and sign in (201) |
| POST | `/auth/login` | Same error for unknown email and wrong password |
| POST | `/auth/logout` | Clear the cookie (204) |
| GET | `/auth/me` | Current user |
| GET | `/me/usage` | AI actions used in the last 24 hours and the daily limit |
| POST | `/me/delete` | Delete the account and all its data (re-checks the password) |
| GET, POST | `/sessions` | List / create prep sessions (capped per user) |
| GET, DELETE | `/sessions/{id}` | Read / archive one |
| GET, POST | `/sessions/{id}/documents` | List / upload a PDF (`file`, `doc_type`) |
| POST | `/sessions/{id}/documents/text` | Index pasted text (same splitter and vector store as a PDF) |
| DELETE | `/sessions/{id}/documents/{doc_id}` | Remove a document and its vectors |
| POST | `/sessions/{id}/chat` | `rag_graph.invoke`, returns answer, sources, retrieval counts |
| GET | `/sessions/{id}/resume` | Latest saved review |
| POST | `/sessions/{id}/resume/check` | `resume_graph.invoke` |
| POST | `/sessions/{id}/theory/start` | `generate_grounded_question`, opens a round |
| POST | `/sessions/{id}/theory/{thread}/answer` | `interview_graph.invoke` for the current question or follow-up |
| POST | `/sessions/{id}/dsa/problem` | `dsa_graph.invoke` (fetches a problem) |
| POST | `/sessions/{id}/dsa/{problem}/submit` | `dsa_graph.invoke` (reviews code) |
| GET | `/sessions/{id}/dashboard` | The same analytics the Streamlit dashboard shows |
| POST | `/sessions/{id}/dashboard/recommendation` | `generate_recommendation` |

Theory rounds and DSA problems keep their graph state on the server (opaque id in the browser), so a visitor
can never feed tampered state back into the graphs. It is per process and expires after 2 hours.

## Guardrails

| Limit | Default | Setting |
|---|---|---|
| AI actions per account per minute | 10 | `API_AI_PER_MINUTE` |
| AI actions per account per 24 h | 40 | `API_AI_PER_DAY` |
| AI actions across the whole site per 24 h (the bill cutoff) | 600 | `API_AI_GLOBAL_PER_DAY` |
| Prep sessions per account | 3 | `API_MAX_SESSIONS_PER_USER` |
| Documents per session | 5 | `API_MAX_DOCS_PER_SESSION` |
| Upload size / PDF pages / pasted text | 5 MB / 40 / 20,000 chars | `API_MAX_UPLOAD_MB`, `API_MAX_PDF_PAGES`, `API_MAX_TEXT_CHARS` |
| Sign-ups per address per hour; logins per address / email | 5; 20 per 10 min / 8 per 15 min | built in |

Only real AI calls count: rejected, invalid or not-yours requests do not use the allowance. Usage is stored in the
`api_usage_events` table, so limits survive restarts. See `deploy/README.md` for expiry and deployment.

## Security notes

- Login is an HttpOnly, SameSite cookie holding a signed, expiring token. It never contains a password.
- Every session route checks ownership; another user's session id looks identical to one that does not exist.
- Writes (`POST`, `DELETE`) are refused when the `Origin` header is not in `API_ALLOWED_ORIGINS`.
- Emails are matched exactly as stored (the existing `auth_service` does not lowercase them).

## Tests

```powershell
.venv\Scripts\python -m unittest discover -s tests_api -t . -p "test_*.py"
```

The tests use a throwaway SQLite file. `tests_api/__init__.py` points the database there before anything else is
imported, and `tests_api/helpers.py` refuses to run if the database in use is anything else, because some tests
delete accounts. **Never run test files directly or from another folder.**

`tests_api/live_smoke.py` is different: it drives a RUNNING API with real embeddings and real LLM calls. Start the API with `python -m api.dev`
(throwaway data), then run it.
