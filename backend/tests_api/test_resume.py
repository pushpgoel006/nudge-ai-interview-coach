"""Section 6 checks: resume route wraps resume_graph like ui/resume_page.py."""

import unittest
from unittest.mock import patch

from tests_api.helpers import ORIGIN, make_session, new_client, register

REVIEW = {
    "id": 1,
    "session_id": "x",
    "overall_score": 72,
    "matched_skills": ["REST"],
    "missing_skills": ["Kubernetes"],
    "suggestions": "Add a Kubernetes project.",
    "created_at": None,
    "verdicts": [
        {"requirement": "REST", "verdict": "clearly demonstrated", "evidence": "Built REST APIs."},
        {"requirement": "Kubernetes", "verdict": "not demonstrated"},
    ],
}


class ResumeTests(unittest.TestCase):
    def test_run_returns_review_and_calls_graph_with_session_id(self):
        with new_client() as c, patch("api.routes.resume.resume_graph") as graph:
            graph.invoke.return_value = {"review": REVIEW}
            register(c, "res1@example.com")
            s = make_session(c)
            r = c.post(f"/api/sessions/{s['id']}/resume/check", headers=ORIGIN)
            self.assertEqual(r.status_code, 200, r.text)
            graph.invoke.assert_called_once_with({"session_id": s["id"]})
            body = r.json()
            self.assertEqual(body["overall_score"], 72)
            self.assertEqual(body["verdicts"][1]["verdict"], "not demonstrated")
            self.assertNotIn("session_id", body)

    def test_missing_documents_is_a_clear_422(self):
        with new_client() as c, patch("api.routes.resume.resume_graph") as graph:
            graph.invoke.return_value = {"review": {"error": "Upload a resume to this session before running the check."}}
            register(c, "res2@example.com")
            s = make_session(c)
            r = c.post(f"/api/sessions/{s['id']}/resume/check", headers=ORIGIN)
            self.assertEqual(r.status_code, 422)
            self.assertIn("Upload a resume", r.json()["detail"])

    def test_latest_is_null_then_saved_review(self):
        from services.resume_service import save_review

        with new_client() as c:
            register(c, "res3@example.com")
            s = make_session(c)
            self.assertIsNone(c.get(f"/api/sessions/{s['id']}/resume").json())
            save_review(s["id"], 55, ["A"], ["B"], "Do more.")
            saved = c.get(f"/api/sessions/{s['id']}/resume").json()
            self.assertEqual((saved["overall_score"], saved["matched_skills"], saved["missing_skills"]), (55, ["A"], ["B"]))
            self.assertIsNone(saved["verdicts"])

    def test_ownership_and_login(self):
        with new_client() as alice, new_client() as bob, new_client() as anon, patch("api.routes.resume.resume_graph") as graph:
            register(alice, "res4a@example.com")
            register(bob, "res4b@example.com")
            s = make_session(alice)
            self.assertEqual(bob.post(f"/api/sessions/{s['id']}/resume/check", headers=ORIGIN).status_code, 404)
            self.assertEqual(bob.get(f"/api/sessions/{s['id']}/resume").status_code, 404)
            self.assertEqual(anon.post(f"/api/sessions/{s['id']}/resume/check", headers=ORIGIN).status_code, 401)
            graph.invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
