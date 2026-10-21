"""Section 10 checks: quotas, throttling, size caps, delete-my-data and account expiry."""

import unittest
from dataclasses import replace
from datetime import datetime, timedelta
from unittest.mock import patch

from api import usage
from api.data import delete_user_everything, purge_expired_accounts
from api.deps import get_settings
from api.main import app
from database.db import get_db
from database.models import Document, DsaAttempt, Followup, Interview, PrepSession, ResumeReview, User
from services.auth_service import get_user
from services.dsa_service import record_attempt
from services.interview_service import record_followup, record_interview
from services.resume_service import save_review
from services.session_service import list_documents, list_sessions, record_document
from tests_api.helpers import ORIGIN, make_session, new_client, register

REVIEW = {"id": 1, "overall_score": 60, "matched_skills": [], "missing_skills": [], "suggestions": "", "created_at": None, "verdicts": []}


class limits:
    """Temporarily swap in different limits, as an environment variable would."""

    def __init__(self, **changes):
        self.changes = changes

    def __enter__(self):
        base = get_settings()
        app.dependency_overrides[get_settings] = lambda: replace(base, **self.changes)

    def __exit__(self, *exc):
        app.dependency_overrides.pop(get_settings, None)


def run_check(c, session_id):
    return c.post(f"/api/sessions/{session_id}/resume/check", headers=ORIGIN)


class QuotaTests(unittest.TestCase):
    def setUp(self):
        p = patch("api.routes.resume.resume_graph")
        self.graph = p.start()
        self.graph.invoke.return_value = {"review": REVIEW}
        self.addCleanup(p.stop)

    def test_burst_limit_per_minute(self):
        with new_client() as c:
            register(c, "q1@example.com")
            s = make_session(c)
            codes = [run_check(c, s["id"]).status_code for _ in range(11)]
            self.assertEqual(codes, [200] * 10 + [429])
            r = run_check(c, s["id"])
            self.assertEqual(r.status_code, 429)
            self.assertIn("Retry-After", r.headers)

    def test_daily_allowance_per_account(self):
        with limits(ai_per_day=2, ai_per_minute=100), new_client() as c:
            register(c, "q2@example.com")
            s = make_session(c)
            self.assertEqual([run_check(c, s["id"]).status_code for _ in range(3)], [200, 200, 429])
            u = c.get("/api/me/usage").json()
            self.assertEqual((u["used_today"], u["limit_today"]), (2, 2))

    def test_global_daily_cutoff_protects_the_bill(self):
        base = usage.count_all_since(86400)
        with limits(ai_global_per_day=base + 2, ai_per_minute=100, ai_per_day=100):
            with new_client() as a, new_client() as b:
                register(a, "q3a@example.com")
                register(b, "q3b@example.com")
                sa, sb = make_session(a), make_session(b)
                self.assertEqual(run_check(a, sa["id"]).status_code, 200)
                self.assertEqual(run_check(b, sb["id"]).status_code, 200)
                r = run_check(a, sa["id"])
                self.assertEqual(r.status_code, 503)
                self.assertIn("budget", r.json()["detail"])

    def test_rejected_requests_do_not_spend_the_allowance(self):
        with patch("api.routes.chat.rag_graph"), new_client() as alice, new_client() as bob:
            register(alice, "q4a@example.com")
            register(bob, "q4b@example.com")
            s = make_session(alice)
            for _ in range(10):
                alice.post(f"/api/sessions/{s['id']}/chat", json={"question": "x"}, headers=ORIGIN)  # invalid body
                alice.post(f"/api/sessions/{s['id']}/chat", json={"question": "valid question"}, headers=ORIGIN)  # no documents
                bob.post(f"/api/sessions/{s['id']}/chat", json={"question": "valid question"}, headers=ORIGIN)  # not his session
            self.assertEqual(alice.get("/api/me/usage").json()["used_today"], 0)
            self.assertEqual(bob.get("/api/me/usage").json()["used_today"], 0)


class ThrottleAndSizeTests(unittest.TestCase):
    def test_sign_up_is_throttled_per_address(self):
        with new_client() as c:
            codes = []
            for n in range(6):
                r = c.post("/api/auth/register", json={"email": f"thr{n}@example.com", "password": "correct-horse", "display_name": "T"}, headers=ORIGIN)
                codes.append(r.status_code)
            self.assertEqual(codes, [201] * 5 + [429])

    def test_login_is_throttled_per_email(self):
        with new_client() as c:
            register(c, "guess@example.com")
            codes = [
                c.post("/api/auth/login", json={"email": "guess@example.com", "password": f"wrong-{n}-pass"}, headers=ORIGIN).status_code
                for n in range(10)
            ]
            self.assertEqual(codes[:8], [401] * 8)
            self.assertEqual(codes[8:], [429, 429])

    def test_forwarded_address_is_used_so_one_proxy_does_not_block_everyone(self):
        with new_client() as c:
            for n in range(6):
                r = c.post(
                    "/api/auth/register",
                    json={"email": f"fwd{n}@example.com", "password": "correct-horse", "display_name": "F"},
                    headers={**ORIGIN, "X-Forwarded-For": f"203.0.113.{n}"},
                )
                self.assertEqual(r.status_code, 201)

    def test_session_cap_per_user(self):
        with new_client() as c:
            register(c, "cap@example.com")
            made = [make_session(c, f"Co{n}", "Role") for n in range(3)]
            over = c.post("/api/sessions", json={"company_name": "Four", "role": "R"}, headers=ORIGIN)
            self.assertEqual(over.status_code, 409)
            c.delete(f"/api/sessions/{made[0]['id']}", headers=ORIGIN)
            self.assertEqual(c.post("/api/sessions", json={"company_name": "Four", "role": "R"}, headers=ORIGIN).status_code, 201)

    def test_oversized_body_is_refused_before_reading(self):
        with new_client() as c:
            r = c.post("/api/auth/login", content=b"x" * (7 * 1024 * 1024), headers={**ORIGIN, "Content-Type": "application/json"})
            self.assertEqual(r.status_code, 413)

    def test_nosniff_header(self):
        with new_client() as c:
            self.assertEqual(c.get("/api/health").headers.get("x-content-type-options"), "nosniff")


def seed_everything(user_id: str) -> str:
    """Give a user one of every kind of record. Returns the session id."""
    from services.session_service import create_session

    s = create_session(user_id, "Acme", "Engineer", "jd")
    sid = s["id"]
    record_document(sid, "resume.pdf", "", "resume", 2)
    iv = record_interview(sid, "apis", "Q", "A", 7, "", "", "")
    record_followup(iv["id"], 1, "apis", "FQ", "FA", 6)
    save_review(sid, 70, ["a"], ["b"], "")
    record_attempt(sid, "array", "easy", "two-sum", "Two Sum", "code", "python", 8, "", "", "")
    usage.record(user_id, "ai")
    return sid


def counts_for(session_id: str) -> dict:
    with get_db() as db:
        iv_ids = [i.id for i in db.query(Interview).filter(Interview.session_id == session_id)]
        return {
            "documents": db.query(Document).filter(Document.session_id == session_id).count(),
            "interviews": len(iv_ids),
            "followups": db.query(Followup).filter(Followup.interview_id.in_(iv_ids)).count() if iv_ids else 0,
            "reviews": db.query(ResumeReview).filter(ResumeReview.session_id == session_id).count(),
            "attempts": db.query(DsaAttempt).filter(DsaAttempt.session_id == session_id).count(),
            "sessions": db.query(PrepSession).filter(PrepSession.id == session_id).count(),
        }


class DeleteDataTests(unittest.TestCase):
    def setUp(self):
        p = patch("api.data.load_vector_store")
        self.vectors = p.start().return_value
        self.vectors.get.return_value = {"ids": ["v1", "v2"]}
        self.addCleanup(p.stop)

    def test_delete_removes_everything_for_that_user_only(self):
        with new_client() as alice, new_client() as bob:
            a = register(alice, "del-a@example.com")
            b = register(bob, "del-b@example.com")
            sa, sb = seed_everything(a["id"]), seed_everything(b["id"])
            self.assertTrue(all(v == 1 for v in counts_for(sa).values()))

            wrong = alice.post("/api/me/delete", json={"password": "not-my-password"}, headers=ORIGIN)
            self.assertEqual(wrong.status_code, 403)
            self.assertIsNotNone(get_user(a["id"]))

            ok = alice.post("/api/me/delete", json={"password": "correct-horse"}, headers=ORIGIN)
            self.assertEqual(ok.status_code, 204)
            self.assertTrue(all(v == 0 for v in counts_for(sa).values()), counts_for(sa))
            self.assertIsNone(get_user(a["id"]))
            self.assertEqual(usage.count_user_since(a["id"], 86400), 0)
            self.vectors.delete.assert_called_with(ids=["v1", "v2"])
            self.assertEqual(alice.get("/api/auth/me").status_code, 401)

            # Bob's data is untouched.
            self.assertTrue(all(v == 1 for v in counts_for(sb).values()))
            self.assertIsNotNone(get_user(b["id"]))
            self.assertEqual(len(list_sessions(b["id"])), 1)
            self.assertEqual(len(list_documents(sb)), 1)

    def test_delete_requires_login_and_a_password(self):
        with new_client() as anon, new_client() as c:
            self.assertEqual(anon.post("/api/me/delete", json={"password": "x"}, headers=ORIGIN).status_code, 401)
            register(c, "del-c@example.com")
            self.assertEqual(c.post("/api/me/delete", json={}, headers=ORIGIN).status_code, 422)

    def test_vector_store_trouble_does_not_block_account_deletion(self):
        self.vectors.get.side_effect = RuntimeError("store offline")
        with new_client() as c:
            u = register(c, "del-d@example.com")
            seed_everything(u["id"])
            self.assertEqual(c.post("/api/me/delete", json={"password": "correct-horse"}, headers=ORIGIN).status_code, 204)
            self.assertIsNone(get_user(u["id"]))


class ExpiryTests(unittest.TestCase):
    def setUp(self):
        p = patch("api.data.load_vector_store")
        p.start().return_value.get.return_value = {"ids": []}
        self.addCleanup(p.stop)

    def age(self, user_id, days):
        with get_db() as db:
            db.query(User).filter(User.id == user_id).update({"created_at": datetime.utcnow() - timedelta(days=days)})

    def test_old_accounts_are_purged_except_the_kept_ones(self):
        with new_client() as c1, new_client() as c2, new_client() as c3:
            old = register(c1, "exp-old@example.com")
            keep = register(c2, "exp-keep@example.com")
            fresh = register(c3, "exp-fresh@example.com")
            sid_old = seed_everything(old["id"])
            self.age(old["id"], 30)
            self.age(keep["id"], 30)

            self.assertEqual(purge_expired_accounts(0), 0)  # disabled
            removed = purge_expired_accounts(14, keep_emails=("exp-keep@example.com",))
            self.assertGreaterEqual(removed, 1)
            self.assertIsNone(get_user(old["id"]))
            self.assertTrue(all(v == 0 for v in counts_for(sid_old).values()))
            self.assertIsNotNone(get_user(keep["id"]))
            self.assertIsNotNone(get_user(fresh["id"]))

    def test_helper_deletes_a_user_with_no_data(self):
        with new_client() as c:
            u = register(c, "exp-empty@example.com")
            self.assertEqual(delete_user_everything(u["id"]), 0)
            self.assertIsNone(get_user(u["id"]))


if __name__ == "__main__":
    unittest.main()
