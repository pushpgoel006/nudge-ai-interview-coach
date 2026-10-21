"""Signed, expiring login tokens (standard library only).

The cookie holds {user id, expiry} plus an HMAC-SHA256 signature. It carries no
password and nothing secret, and a tampered or expired token is rejected.
"""

import base64
import hashlib
import hmac
import json
import time


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _signature(secret: str, body: str) -> str:
    return _b64(hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest())


def create_token(user_id: str, secret: str, ttl_seconds: int, now: float | None = None) -> str:
    issued = time.time() if now is None else now
    payload = {"uid": user_id, "exp": int(issued) + ttl_seconds}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return f"{body}.{_signature(secret, body)}"


def read_token(token: str, secret: str, now: float | None = None) -> str | None:
    """Return the user id if the token is genuine and unexpired, else None."""
    try:
        body, signature = token.split(".", 1)
        if not hmac.compare_digest(signature, _signature(secret, body)):
            return None
        payload = json.loads(_unb64(body))
        current = time.time() if now is None else now
        if int(payload["exp"]) < current:
            return None
        user_id = payload["uid"]
        return user_id if isinstance(user_id, str) and user_id else None
    except (ValueError, KeyError, TypeError):
        return None
