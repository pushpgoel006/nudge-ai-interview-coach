"""One place that runs the existing graphs/agents and turns failures into clean HTTP errors."""

import logging
from collections.abc import Callable
from typing import TypeVar

from fastapi import HTTPException, status

log = logging.getLogger("nudge.api")
T = TypeVar("T")


def run_ai(fn: Callable[..., T], *args, **kwargs) -> T:
    """Call an existing graph or agent. Any failure inside the LLM or retrieval stack is logged
    in full on the server and reported to the browser as a generic, retryable error."""
    try:
        return fn(*args, **kwargs)
    except HTTPException:
        raise
    except Exception:
        log.exception("AI call failed")
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, "The AI service hit a problem. Please try again in a moment."
        ) from None
