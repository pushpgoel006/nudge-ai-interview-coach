# Deploying Nudge

Two pieces: the **API** (this project, on a Hugging Face Space) and the **site** (`nudge-web`, on Vercel).
No existing backend file is changed for this. Everything here is new.

## 0. Before you go public

1. **Check the production database you are pointing at.** The API reads `DATABASE_URL` exactly like
   the Streamlit app, so the Space will use whatever database that URL names (your Neon database).
   The API adds one small table, `api_usage_events`, on first start.
2. **Decide who the demo is for.** Anyone can sign up. The limits below keep that safe; tune them.

## 1. API on Hugging Face Spaces

1. Create a new Space: SDK **Docker**, hardware **CPU basic (free)**.
2. Put the backend code in the Space repo, then add the three deployment files at its root:

   | From this repo | To the Space repo root |
   |---|---|
   | `deploy/huggingface/Dockerfile` | `Dockerfile` |
   | `deploy/huggingface/README.md` | `README.md` (replaces the project README **in the Space only**) |
   | `deploy/huggingface/dockerignore.txt` | `.dockerignore` |

   Keep `deploy/huggingface/start.sh` where it is. Do **not** copy `.env`, `.venv`, `uploads/` or `chroma_db/`.
3. In the Space **Settings → Variables and secrets**, add as **secrets**:

   | Secret | Value |
   |---|---|
   | `DATABASE_URL` | your Neon connection string |
   | `GROQ_API_KEY` | your Groq key |
   | `API_SECRET_KEY` | a long random string, for example `python -c "import secrets;print(secrets.token_urlsafe(48))"` |
   | `API_ALLOWED_ORIGINS` | your site origin, for example `https://nudge.vercel.app` (no trailing slash) |

   Optional (defaults in brackets): `API_AI_PER_DAY` [40], `API_AI_PER_MINUTE` [10], `API_AI_GLOBAL_PER_DAY` [600],
   `API_MAX_SESSIONS_PER_USER` [3], `API_MAX_DOCS_PER_SESSION` [5], `API_MAX_UPLOAD_MB` [5], `API_MAX_PDF_PAGES` [40],
   `API_ACCOUNT_TTL_DAYS` [0 = off], `API_ACCOUNT_KEEP_EMAILS`.
4. Wait for the build (the first one is slow: it installs PyTorch CPU and downloads the embedding model).
5. Check `https://<your-space>.hf.space/api/health?deep=true` returns `{"status":"ok","database":"ok"}`.

### Keeping uploaded documents across restarts

The free Space disk is **wiped on every restart or sleep**. Your accounts, sessions and scores live in Neon
and survive, but the indexed document text is in a local Chroma folder and does not. Until you fix that, a
restart leaves documents marked "Needs re-adding" in the UI (the API detects this) and visitors re-upload.

Two ways to fix it:

- **Attach Hugging Face persistent storage** (paid, a few dollars a month). `start.sh` already links
  `chroma_db` to `/data/chroma_db` when `/data` exists. No code change.
- **Move the vector store to Chroma Cloud or pgvector on Neon.** Better long-term, but it edits
  `rag/vector_store.py` and `rag/retriever.py`, which you asked me not to touch, so I have not done it.

### Auto-expiring demo accounts (optional)

```powershell
# preview what would go (deletes nothing)
.venv\Scripts\python -m api.cleanup --days 14 --keep you@example.com
# delete for real
.venv\Scripts\python -m api.cleanup --days 14 --keep you@example.com --yes
```

Or set `API_ACCOUNT_TTL_DAYS=14` and `API_ACCOUNT_KEEP_EMAILS=you@example.com` on the Space to purge at start-up.
**Both delete every account older than the cutoff, including yours, unless its email is kept.** Run the preview first,
and check which database `DATABASE_URL` points at.

### Alternative: Render (free plan)

Hugging Face now needs a paid plan for Docker Spaces. The repo root has a `render.yaml` Blueprint that builds the same
Dockerfile on Render:

1. Render dashboard: **New + > Blueprint**, connect GitHub, pick this repo. Render reads `render.yaml`.
2. When asked, enter the two secrets: `GROQ_API_KEY` and `DATABASE_URL` (a Neon connection string, ideally a
   separate demo database). `API_SECRET_KEY` is generated for you.
3. After the first deploy, `https://<service>.onrender.com/api/health?deep=true` should return
   `{"status":"ok","database":"ok"}`.

Limits of the free plan: 512 MB of memory (the embedding model is a tight fit; measured peak was about 500 MB
resident when run locally), the service sleeps after 15 minutes without traffic and takes about a minute to wake,
and there is no persistent disk, so indexed documents are lost on every restart (the API marks them
"Needs re-adding"). Accounts, sessions and scores live in Neon and survive.

## 2. Site on Vercel

1. Import the `nudge-web` folder as a project (framework: Next.js).
2. Environment variables:

   | Variable | Value |
   |---|---|
   | `BACKEND_URL` | `https://<your-space>.hf.space` |
   | `NEXT_PUBLIC_APP_URL` | leave unset (the Launch button opens `/studio`) |

3. Deploy. `/api/*` on your site is forwarded to the Space, so cookies stay first-party and the Space URL never
   appears in the browser.
4. Put the final Vercel URL into the Space's `API_ALLOWED_ORIGINS` and restart it. Until you do, sign-up and other
   writes are refused with "Origin not allowed".

## 3. Smoke test the live site

From the backend project, with a **throwaway** account (the script registers one and deletes it at the end):

```powershell
.venv\Scripts\python tests_api\live_smoke.py https://<your-site>.vercel.app
```

It makes about a dozen real LLM calls. If it prints `ALL STAGES PASSED`, sign-up, upload, chat, resume check,
theory round, DSA round, dashboard and delete-my-data all work through Vercel and the Space.

## Local development

From the `nudge-web` folder, one command starts the site and the API together (the API on throwaway data,
never your real database):

```powershell
npm run dev:all
```
