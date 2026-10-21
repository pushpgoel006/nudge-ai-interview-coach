"""HTTP layer for the Nudge site.

This only exposes the existing services and LangGraph graphs over HTTP. It does not
change how documents are loaded or how the graphs and LLM calls run.

Run from the project root:
    python -m uvicorn api.main:app --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from api import usage
from api.data import purge_expired_accounts
from api.deps import get_settings
from api.routes import account, auth, chat, dashboard, documents, dsa, resume, sessions, theory
from database import models  # noqa: F401  (registers the tables on Base)
from database.db import Base, DATABASE_URL, engine

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Same idempotent create_all that database/init_db.py runs. Hosted Postgres is
    # assumed to be set up already; only local SQLite is created automatically.
    if DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    usage.ensure_table()  # the API's one extra table, created if missing
    usage.prune_older_than(3)
    settings = get_settings()
    if settings.account_ttl_days > 0:
        purge_expired_accounts(settings.account_ttl_days, settings.keep_emails)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Nudge API",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if settings.docs_enabled else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.middleware("http")
    async def reject_foreign_origins(request: Request, call_next):
        # Browsers always send Origin on cross-site POST/DELETE. Refuse any that is not ours.
        origin = request.headers.get("origin")
        if request.method not in SAFE_METHODS and origin and origin.rstrip("/") not in settings.allowed_origins:
            return JSONResponse({"detail": "Origin not allowed."}, status_code=403)
        return await call_next(request)

    @app.middleware("http")
    async def guard_body_size_and_sniffing(request: Request, call_next):
        # Refuse oversized bodies before they are read into memory (uploads are capped separately).
        declared = request.headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > settings.max_upload_bytes + 1024 * 1024:
            return JSONResponse({"detail": "That request is too large."}, status_code=413)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    api = APIRouter(prefix="/api")

    @api.get("/health", tags=["health"])
    def health(deep: bool = False):
        result = {"status": "ok"}
        if deep:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            result["database"] = "ok"
        return result

    api.include_router(auth.router)
    api.include_router(account.router)
    api.include_router(sessions.router)
    api.include_router(documents.router)
    api.include_router(chat.router)
    api.include_router(resume.router)
    api.include_router(theory.router)
    api.include_router(dsa.router)
    api.include_router(dashboard.router)
    app.include_router(api)
    return app


app = create_app()
