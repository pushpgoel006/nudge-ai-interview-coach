"""Small in-memory sliding-window limiter for sign-in and sign-up attempts.

Per process, which is right for a single-instance deployment. A restart clears it, so the
durable limits (AI usage) live in the database instead.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class SlidingWindow:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        t = time.time() if now is None else now
        with self._lock:
            q = self._hits[key]
            while q and t - q[0] > self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(t)
            if len(self._hits) > 5000:  # keep memory bounded
                for k in [k for k, v in self._hits.items() if not v or t - v[-1] > self.window][:1000]:
                    self._hits.pop(k, None)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def client_ip(request: Request) -> str:
    """The visitor's address. Behind the Vercel rewrite and the host's proxy the socket address is
    the proxy, so the first X-Forwarded-For entry is used. A determined attacker can spoof it, which
    only lets them dodge this soft limit; the per-account AI quotas do not depend on it."""
    forwarded = request.headers.get("x-forwarded-for", "")
    first = forwarded.split(",")[0].strip()
    return first or (request.client.host if request.client else "unknown")


login_by_ip = SlidingWindow(limit=20, window_seconds=600)
login_by_email = SlidingWindow(limit=8, window_seconds=900)
register_by_ip = SlidingWindow(limit=5, window_seconds=3600)


def too_many(retry_after: int) -> HTTPException:
    return HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Too many attempts. Please wait a few minutes and try again.",
        headers={"Retry-After": str(retry_after)},
    )
