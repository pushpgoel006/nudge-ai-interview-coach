"""Shared FastAPI dependencies: settings, the logged-in user, and session ownership."""

from collections.abc import Callable
from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status

from api import usage

from api.config import Settings, load_settings
from api.security import read_token
from services.auth_service import get_user
from services.session_service import get_session


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()


def current_user(request: Request, settings: Settings = Depends(get_settings)) -> dict:
    token = request.cookies.get(settings.cookie_name)
    user_id = read_token(token, settings.secret_key) if token else None
    user = get_user(user_id) if user_id else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in to continue.")
    return user


def owned_session(session_id: str, user: dict = Depends(current_user)) -> dict:
    """The prep session, only if it belongs to the logged-in user. Anything else is a 404,
    so one user cannot tell whether another user's session id exists."""
    session = get_session(session_id, user["id"])
    if session is None or session["status"] == "archived":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found.")
    return session


def ai_budget(user: dict = Depends(current_user), settings: Settings = Depends(get_settings)) -> Callable[[], None]:
    """Gives a route a `spend()` function to call right before it spends an LLM call (or reaches an
    outside service on the user's behalf). Calling it after validation, ownership and precondition
    checks means rejected requests never use up the allowance.

    Checked in order: a per-minute burst limit, the account's daily allowance, then the site-wide
    daily cutoff that protects the API bill. The attempt is recorded before the work starts, so
    retrying a failing call still counts."""

    def spend() -> None:
        if usage.count_user_since(user["id"], 60) >= settings.ai_per_minute:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, "That was a lot at once. Give it a moment and try again.", headers={"Retry-After": "30"}
            )
        if usage.count_user_since(user["id"], 86400) >= settings.ai_per_day:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"You have used today's {settings.ai_per_day} AI actions. The allowance refills over the next 24 hours.",
                headers={"Retry-After": "3600"},
            )
        if usage.count_all_since(86400) >= settings.ai_global_per_day:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "The demo has reached its AI budget for today. Please come back tomorrow.",
                headers={"Retry-After": "3600"},
            )
        usage.record(user["id"], "ai")

    return spend
