"""Section 2 checks: health, login cookie, session ownership, and basic abuse guards.

Run from the project root:
    .venv\\Scripts\\python -m unittest tests_api.test_foundation -v

Uses a throwaway SQLite file, never your real database.
"""

import time
import unittest

from api.security import create_token, read_token
from tests_api.helpers import ORIGIN, new_client


class TokenTests(unittest.TestCase):
    def test_round_trip(self):
        token = create_token("user-1", "s", 60)
        self.assertEqual(read_token(token, "s"), "user-1")

    def test_wrong_secret_rejected(self):
        self.assertIsNone(read_token(create_token("user-1", "s", 60), "other"))

    def test_tampered_rejected(self):
        body, sig = create_token("user-1", "s", 60).split(".")
        self.assertIsNone(read_token(f"{body}x.{sig}", "s"))
        self.assertIsNone(read_token("garbage", "s"))
        self.assertIsNone(read_token("", "s"))

    def test_expired_rejected(self):
        old = create_token("user-1", "s", 60, now=time.time() - 3600)
        self.assertIsNone(read_token(old, "s"))


class ApiTests(unittest.TestCase):
    def register(self, client, email="a@example.com", name="Alex", password="correct-horse"):
        return client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "display_name": name},
            headers=ORIGIN,
        )

    def test_health(self):
        with new_client() as c:
            self.assertEqual(c.get("/api/health").json(), {"status": "ok"})
            self.assertEqual(c.get("/api/health", params={"deep": "true"}).json()["database"], "ok")

    def test_register_sets_httponly_cookie_and_hides_secrets(self):
        with new_client() as c:
            r = self.register(c, "reg@example.com")
            self.assertEqual(r.status_code, 201)
            self.assertEqual(set(r.json()), {"id", "email", "display_name"})
            cookie = r.headers["set-cookie"].lower()
            self.assertIn("httponly", cookie)
            self.assertIn("samesite=lax", cookie)
            self.assertEqual(c.get("/api/auth/me").json()["email"], "reg@example.com")

    def test_duplicate_email_conflict(self):
        with new_client() as c:
            self.register(c, "dup@example.com")
            self.assertEqual(self.register(c, "dup@example.com").status_code, 409)

    def test_login_wrong_password_is_generic(self):
        with new_client() as c:
            self.register(c, "login@example.com")
        with new_client() as c:
            bad = c.post("/api/auth/login", json={"email": "login@example.com", "password": "nope-nope"}, headers=ORIGIN)
            ghost = c.post("/api/auth/login", json={"email": "ghost@example.com", "password": "nope-nope"}, headers=ORIGIN)
            self.assertEqual(bad.status_code, 401)
            self.assertEqual(bad.json(), ghost.json())
            ok = c.post("/api/auth/login", json={"email": "login@example.com", "password": "correct-horse"}, headers=ORIGIN)
            self.assertEqual(ok.status_code, 200)
            self.assertEqual(c.get("/api/auth/me").status_code, 200)

    def test_logout_clears_login(self):
        with new_client() as c:
            self.register(c, "out@example.com")
            self.assertEqual(c.post("/api/auth/logout", headers=ORIGIN).status_code, 204)
            self.assertEqual(c.get("/api/auth/me").status_code, 401)

    def test_input_limits(self):
        with new_client() as c:
            self.assertEqual(self.register(c, "short@example.com", password="short").status_code, 422)
            self.assertEqual(self.register(c, "long@example.com", password="x" * 73).status_code, 422)
            extra = c.post(
                "/api/auth/register",
                json={"email": "e@example.com", "password": "correct-horse", "display_name": "E", "admin": True},
                headers=ORIGIN,
            )
            self.assertEqual(extra.status_code, 422)

    def test_requires_login(self):
        with new_client() as c:
            self.assertEqual(c.get("/api/sessions").status_code, 401)
            self.assertEqual(c.get("/api/auth/me").status_code, 401)

    def test_tampered_cookie_rejected(self):
        with new_client() as c:
            self.register(c, "tamper@example.com")
            c.cookies.set("nudge_session", "forged.value")
            self.assertEqual(c.get("/api/auth/me").status_code, 401)

    def test_foreign_origin_blocked_on_writes(self):
        with new_client() as c:
            r = c.post(
                "/api/auth/login",
                json={"email": "x@example.com", "password": "whatever1"},
                headers={"Origin": "https://evil.example"},
            )
            self.assertEqual(r.status_code, 403)

    def test_sessions_crud_and_ownership(self):
        with new_client() as alice, new_client() as bob:
            self.register(alice, "alice@example.com", "Alice")
            self.register(bob, "bob@example.com", "Bob")

            made = alice.post(
                "/api/sessions",
                json={"company_name": "Acme", "role": "Backend Engineer", "jd_text": "Python, SQL"},
                headers=ORIGIN,
            )
            self.assertEqual(made.status_code, 201)
            session = made.json()
            self.assertNotIn("owner_id", session)

            self.assertEqual([s["id"] for s in alice.get("/api/sessions").json()], [session["id"]])
            self.assertEqual(bob.get("/api/sessions").json(), [])
            self.assertEqual(alice.get(f"/api/sessions/{session['id']}").status_code, 200)

            # Bob cannot read or archive Alice's session, and cannot tell it exists.
            self.assertEqual(bob.get(f"/api/sessions/{session['id']}").status_code, 404)
            self.assertEqual(bob.delete(f"/api/sessions/{session['id']}", headers=ORIGIN).status_code, 404)
            self.assertEqual(bob.get("/api/sessions/does-not-exist").status_code, 404)

            self.assertEqual(alice.delete(f"/api/sessions/{session['id']}", headers=ORIGIN).status_code, 204)
            self.assertEqual(alice.get(f"/api/sessions/{session['id']}").status_code, 404)
            self.assertEqual(alice.get("/api/sessions").json(), [])

    def test_session_validation(self):
        with new_client() as c:
            self.register(c, "val@example.com")
            blank = c.post("/api/sessions", json={"company_name": "  ", "role": "x"}, headers=ORIGIN)
            self.assertEqual(blank.status_code, 422)
            huge = c.post(
                "/api/sessions",
                json={"company_name": "A", "role": "B", "jd_text": "x" * 20001},
                headers=ORIGIN,
            )
            self.assertEqual(huge.status_code, 422)


if __name__ == "__main__":
    unittest.main()
