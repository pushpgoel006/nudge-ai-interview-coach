"""Shared test helpers: a test client, and small builders.

The throwaway database is configured in `tests_api/__init__.py`. This module refuses to
continue if the database in use is anything other than that throwaway file.
"""

import pymupdf
from fastapi.testclient import TestClient

from database.db import DATABASE_URL, engine
from tests_api import TEST_DB_URL

# Hard stop. A test run must never touch a real database, whatever the import order was.
if DATABASE_URL != TEST_DB_URL or not str(engine.url).startswith("sqlite"):
    raise RuntimeError(
        "Refusing to run tests: the database in use is not the throwaway test database. "
        "Import tests only through the tests_api package."
    )

from api.main import app  # noqa: E402

ORIGIN = {"Origin": "http://localhost:3000"}


def new_client() -> TestClient:
    from api import ratelimit

    for window in (ratelimit.login_by_ip, ratelimit.login_by_email, ratelimit.register_by_ip):
        window.reset()
    return TestClient(app)


def register(client: TestClient, email: str, name: str = "Tester", password: str = "correct-horse"):
    r = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "display_name": name},
        headers=ORIGIN,
    )
    assert r.status_code == 201, r.text
    return r.json()


def make_session(client: TestClient, company: str = "Acme", role: str = "Engineer") -> dict:
    r = client.post("/api/sessions", json={"company_name": company, "role": role}, headers=ORIGIN)
    assert r.status_code == 201, r.text
    return r.json()


def pdf_bytes(text: str = "hello nudge", pages: int = 1) -> bytes:
    doc = pymupdf.open()
    for _ in range(pages):
        doc.new_page().insert_text((72, 72), text)
    return doc.tobytes()
