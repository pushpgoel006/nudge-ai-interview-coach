"""Settings for the HTTP API, read from environment variables.

Nothing here touches the AI pipeline. Secrets stay on the backend host.
"""

import os
import secrets
import warnings
from dataclasses import dataclass


def _flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    env: str
    secret_key: str
    cookie_name: str
    cookie_secure: bool
    cookie_samesite: str
    session_ttl_seconds: int
    allowed_origins: tuple[str, ...]
    docs_enabled: bool
    max_upload_bytes: int
    max_pdf_pages: int
    max_docs_per_session: int
    max_text_chars: int
    max_sessions_per_user: int
    ai_per_minute: int
    ai_per_day: int
    ai_global_per_day: int
    account_ttl_days: int
    keep_emails: tuple[str, ...]


def load_settings() -> Settings:
    env = os.getenv("API_ENV", "development").strip().lower()
    production = env == "production"

    secret = os.getenv("API_SECRET_KEY", "").strip()
    if not secret:
        if production:
            raise RuntimeError("API_SECRET_KEY must be set when API_ENV=production.")
        # Development convenience only: logins are lost whenever the server restarts.
        secret = secrets.token_urlsafe(48)
        warnings.warn(
            "API_SECRET_KEY is not set; using a temporary key. Logins will not survive a restart.",
            stacklevel=2,
        )

    origins = os.getenv("API_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    allowed = tuple(o.strip().rstrip("/") for o in origins.split(",") if o.strip())

    samesite = os.getenv("API_COOKIE_SAMESITE", "lax").strip().lower()
    if samesite not in {"lax", "strict", "none"}:
        samesite = "lax"

    return Settings(
        env=env,
        secret_key=secret,
        cookie_name=os.getenv("API_COOKIE_NAME", "nudge_session"),
        cookie_secure=_flag("API_COOKIE_SECURE", production),
        cookie_samesite=samesite,
        session_ttl_seconds=int(os.getenv("API_SESSION_TTL_DAYS", "7")) * 24 * 3600,
        allowed_origins=allowed,
        docs_enabled=_flag("API_DOCS", not production),
        max_upload_bytes=int(os.getenv("API_MAX_UPLOAD_MB", "5")) * 1024 * 1024,
        max_pdf_pages=int(os.getenv("API_MAX_PDF_PAGES", "40")),
        max_docs_per_session=int(os.getenv("API_MAX_DOCS_PER_SESSION", "5")),
        max_text_chars=int(os.getenv("API_MAX_TEXT_CHARS", "20000")),
        max_sessions_per_user=int(os.getenv("API_MAX_SESSIONS_PER_USER", "3")),
        ai_per_minute=int(os.getenv("API_AI_PER_MINUTE", "10")),
        ai_per_day=int(os.getenv("API_AI_PER_DAY", "40")),
        ai_global_per_day=int(os.getenv("API_AI_GLOBAL_PER_DAY", "600")),
        account_ttl_days=int(os.getenv("API_ACCOUNT_TTL_DAYS", "0")),
        keep_emails=tuple(e.strip() for e in os.getenv("API_ACCOUNT_KEEP_EMAILS", "").split(",") if e.strip()),
    )
