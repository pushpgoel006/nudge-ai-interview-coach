# Nudge (web)

Portfolio site for the Nudge AI interview coach: a scroll-driven landing page and the live studio at `/studio`.

- **Stack:** Next.js (App Router, TypeScript), GSAP + Lenis for motion.
- **Backend:** the Python project (FastAPI over LangChain + LangGraph). This site only talks to it through
  `/api/*`, which `next.config.ts` forwards to `BACKEND_URL`.
- **Plan and status:** [PLAN.md](PLAN.md). **Deploying:** see [`backend/deploy/README.md`](../backend/deploy/README.md).

## Run it

One command starts both the site and the Python API (the API runs on throwaway data, never your real database):

```powershell
npm install          # first time only
npm run dev:all      # site: http://localhost:3000   studio: http://localhost:3000/studio   API: http://127.0.0.1:8000
```

Press Ctrl+C once to stop both. Output is labelled `[web]` and `[api]`. If an API is already running on port 8000 it
is reused. The launcher looks for the backend at `../backend` (the folder next to `web/` in this repo); if it lives
elsewhere set `NUDGE_BACKEND_DIR` to that folder. The backend needs its own Python environment first
(`cd ../backend && uv sync`, or `python -m venv .venv` and `pip install -r requirements.txt`).

Why two processes? The site is JavaScript and the AI code is Python, so they cannot be one program. They are two
servers that this command starts together. To run them separately:

```powershell
# backend project:  .venv\Scripts\python -m api.dev
# here:             npm run dev
```

## Checks

```powershell
npx tsc --noEmit
npm run lint
npm run build
```

## Layout

| Path | What |
|---|---|
| `app/page.tsx`, `components/landing/` | Landing page (server-rendered sections + one client `Motion` component) |
| `app/studio/`, `components/studio/` | The studio. `/studio` (sessions), then one page per tool: `/studio/documents`, `/chat`, `/resume`, `/theory`, `/dsa`, `/dashboard`, linked from the top bar |
| `components/studio/StudioProvider.tsx` | Sign-in, sessions, the current session's documents, and each tool's remembered state (chat history, drafts, DSA code) so moving between pages loses nothing |
| `components/studio/charts/` | Hand-built SVG charts: readiness donut, score trend, topic bars and radar (hover, focus and click interactions, no chart library) |
| `lib/api.ts` | Small typed fetch client for `/api` |
| `public/images/` | Cut-out figures used on the landing page |
